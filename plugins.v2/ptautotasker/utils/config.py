class Config:
    # 原为 5 秒，PT 站点(Cloudflare + DB 查询)经常超过 5s 导致
    # "HTTPSConnectionPool(...): Read timed out. (read timeout=5)"，放宽到 10 秒。
    REQUEST_TIMEOUT = 10  # Default timeout for requests in seconds
