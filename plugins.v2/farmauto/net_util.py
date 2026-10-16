# net_util.py - 网络请求封装
# 跨境/高延迟线路优化（对齐 ptautotasker 的做法）：
#   1. Session + HTTPAdapter 连接池：同一站点多次请求只握手一次，省掉每请求的 TCP+TLS 往返
#   2. 分阶段超时：连接慢快速失败，不白等读取预算
#   3. 瞬时故障自动重试：读取超时 / 连接重置 / DNS 临时失败(Temporary failure in name resolution)等
import time

import requests
from requests.adapters import HTTPAdapter

# 连接超时 / 读取超时 / 重试次数 / 退避基数(秒)
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
RETRY_TIMES = 2
RETRY_BACKOFF = 1.0
POOL_SIZE = 10

_SESSIONS = {}


def get_session(pool_size: int = POOL_SIZE) -> requests.Session:
    """按池大小缓存 Session，跨任务复用连接。"""
    size = pool_size if pool_size and pool_size > 0 else POOL_SIZE
    sess = _SESSIONS.get(size)
    if sess is None:
        sess = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=size,
            pool_maxsize=size,
            max_retries=0,          # 重试由本模块统一控制，避免与业务重试叠加
            pool_block=True,
        )
        sess.mount("http://", adapter)
        sess.mount("https://", adapter)
        _SESSIONS[size] = sess
    return sess


def _is_retryable(exc: Exception) -> bool:
    """仅对瞬时故障重试；HTTP 4xx/5xx 由业务判断，不在此重试。"""
    return isinstance(exc, (
        requests.exceptions.ConnectionError,      # 含 DNS 临时失败
        requests.exceptions.Timeout,
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.ContentDecodingError,
    ))


def request(method: str, url: str, headers=None, cookies=None, params=None, data=None,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), retries: int = RETRY_TIMES,
            retry_backoff: float = RETRY_BACKOFF, verify: bool = False,
            allow_redirects: bool = True, pool_size: int = POOL_SIZE):
    """统一的带重试请求入口。返回 requests.Response。"""
    sess = get_session(pool_size)
    tmo = tuple(timeout) if isinstance(timeout, (tuple, list)) else (CONNECT_TIMEOUT, float(timeout))

    last_exc = None
    for attempt in range(1, max(1, int(retries)) + 2):
        try:
            resp = sess.request(method, url, headers=headers, cookies=cookies,
                                params=params, data=data, timeout=tmo, verify=verify,
                                allow_redirects=allow_redirects)
            # 5xx 视为瞬时故障可重试；4xx 直接返回交由业务处理
            if resp.status_code >= 500 and attempt <= retries:
                last_exc = requests.exceptions.HTTPError(f"HTTP {resp.status_code}")
                time.sleep(retry_backoff * attempt)
                continue
            return resp
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt > retries or not _is_retryable(exc):
                raise
            time.sleep(retry_backoff * attempt)
    raise last_exc if last_exc else requests.exceptions.RequestException("请求失败")


def get(url: str, **kwargs):
    return request("GET", url, **kwargs)


def post(url: str, **kwargs):
    return request("POST", url, **kwargs)


def describe_error(exc: Exception) -> str:
    """把底层异常翻译成可读原因，便于日志区分 超时/DNS/HTTP/连接问题。"""
    name = type(exc).__name__
    if isinstance(exc, requests.exceptions.ConnectTimeout):
        return f"连接超时({CONNECT_TIMEOUT}s 内未完成TCP/TLS 握手)"
    if isinstance(exc, requests.exceptions.ReadTimeout):
        return f"读取超时(连接已建立，但{READ_TIMEOUT}s 内服务器未返回数据)"
    if isinstance(exc, requests.exceptions.SSLError):
        return f"SSL/TLS 握手失败：{str(exc)[:80]}"
    if isinstance(exc, requests.exceptions.ConnectionError):
        msg = str(exc)
        if "name resolution" in msg or "nodename nor servname" in msg or "Temporary failure" in msg:
            return "域名解析失败(DNS 临时故障或容器 DNS 异常)"
        if "Connection refused" in msg:
            return "连接被拒绝(站点可能已关闭或端口不通)"
        return f"连接失败：{msg[:100]}"
    if isinstance(exc, requests.exceptions.HTTPError):
        return f"HTTP 错误：{str(exc)[:80]}"
    return f"{name}: {str(exc)[:120]}"