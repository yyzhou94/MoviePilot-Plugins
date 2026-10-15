from ..base.Decorator import task_info
from ..base.NexusPHP import NexusPHP
from ..utils.custom_requests import CustomRequests
from ..base.BaseTask import BaseTask
from lxml import etree


class Luckpt(NexusPHP):

    def __init__(self, cookie):
        super().__init__(cookie)
        # 勋章收藏页（领取按钮所在页）
        self.medal_page_url = self.url + "/medal_collection.php"
        # ajax.php 由基类提供：self.url_ajax
        # 领取接口（POST ajax.php），参数来自浏览器实际抓取：
        #   action=claimMedalCategoryReward
        #   params[category_id]=<分类id>
        #   params[reward_type]=<奖励类型，如 bonus_daily>
        self.claim_action = "claimMedalCategoryReward"

    @staticmethod
    def get_site_name():
        return "LuckPT"

    @staticmethod
    def get_url():
        return "https://pt.luckpt.de"

    @staticmethod
    def get_site_domain():
        return "pt.luckpt.de"

    def _parse_claim_response(self, response):
        """解析领取响应。返回 (状态, 说明)。
        状态: success / already / fail
        兼容 JSON 与纯文本两种返回；并把原始响应片段回显便于首跑校准。
        """
        text = (response.text or "").strip()
        raw = text[:200]
        if getattr(response, "status_code", 200) != 200:
            return "fail", f"HTTP {response.status_code} | raw: {raw}"
        try:
            data = response.json()
        except Exception:
            data = None

        if data is not None:
            success = data.get("success")
            code = data.get("errorCode")
            if code is None:
                code = data.get("code")
            msg = (data.get("errorMsg") or data.get("msg") or data.get("message") or "")
            msg = str(msg)
            if success is False or (isinstance(code, int) and code not in (0, None)):
                if any(k in msg for k in ("已领取", "已经", "claimed", "already")):
                    return "already", msg or raw
                return "fail", msg or raw
            # success 为 True 或无明确失败标识，均视为成功（请求已完成）
            return "success", (msg or "领取成功") + f" | raw: {raw}"

        # 纯文本回退
        if any(k in text for k in ("已领取", "已经领取", "claimed", "already")):
            return "already", raw
        if "成功" in text or "ok" in text.lower():
            return "success", raw
        return "unknown", raw

    def _claim_one(self, category, reward_type, label):
        data = {
            "action": self.claim_action,
            "params[category_id]": category,
            "params[reward_type]": reward_type,
        }
        try:
            response = CustomRequests.post(self.url_ajax, headers=self.headers, data=data)
        except Exception as e:
            return f"❌ {label}（category={category}）请求异常：{e}"
        status, msg = self._parse_claim_response(response)
        if status == "success":
            return f"✅ {label}（category={category}）领取成功：{msg}"
        elif status == "already":
            return f"ℹ️ {label}（category={category}）今日已领取：{msg}"
        else:
            return f"❌ {label}（category={category}）领取失败：{msg}"

    def medal_bonus(self):
        """领取 LuckPT 勋章奖励。
        先抓取勋章页，自动找出所有可领取的 claim-reward 按钮并逐个领取；
        若页面未直接暴露按钮（懒加载），兜底领取已确认的默认分类(8/bonus_daily)。
        """
        try:
            page = CustomRequests.get(self.medal_page_url, headers=self.headers)
        except Exception as e:
            # 抓不到页面也兜底领一次已知分类，避免漏掉每日奖励
            return self._claim_one("8", "bonus_daily", "每日幸运星 +1000(页面抓取失败兜底)")

        tree = etree.HTML(page.text or "")
        buttons = tree.xpath(
            "//button[contains(concat(' ', normalize-space(@class), ' '), ' claim-reward ')]"
        )

        if not buttons:
            # 兜底：直接领取已确认的默认分类
            return self._claim_one("8", "bonus_daily", "每日幸运星 +1000(未扫描到按钮兜底)")

        results = []
        for btn in buttons:
            category = (btn.get("data-category") or "").strip()
            reward_type = (btn.get("data-type") or "").strip()
            reward_label = (btn.get("data-reward-label") or (btn.text or "")).strip()
            if not category or not reward_type:
                continue
            results.append(self._claim_one(category, reward_type, reward_label or f"分类{category}"))
        return "\n".join(results) if results else "未找到可领取的勋章奖励"


class Tasks(BaseTask):
    def __init__(self, cookie: str):
        super().__init__(Luckpt(cookie))

    @task_info(label="Luckpt勋章奖励", hint="自动领取 LuckPT 站点可领取的勋章套装每日奖励(如每日幸运星+1000)")
    def medal_bonus(self):
        return self.client.medal_bonus()
