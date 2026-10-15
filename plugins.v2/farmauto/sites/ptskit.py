# sites/ptskit.py - 拾刻(PTSKit) 站点配置
# 适配说明：拾刻(PTSKit, www.ptskit.org) 与 HDClone 一样是【定制版】NexusPHP 农场页(magic_farm.php)，
# 但作物/动物恰好与基类默认的 4+4 完全一致（成本也相同），故此处显式声明以便自文档化。
# 依据：真实页面 https://www.ptskit.org/magic_farm.php
#   - 货币：当前魔力值 411,651.0  → currency = "魔力"
#   - 一键收获：<a href="?action=harvest_all">            → 与基类 get_harvest_all_url 一致
#   - 作物卡片：<h3>名称</h3><p>价格: X</p><a href="?action=harvest&type=crop&id=N" class="btn harvest-btn">
#   - 动物卡片：<a href="?action=harvest&type=animal&id=N" class="btn harvest-btn">
#   - 成熟后按钮由 plant/breed 变为 harvest，因此「出现 action=harvest 链接」即代表可收获。
#   - 菜市场：<h2>菜市场</h2> → <div class="market-category"><h3>农作物种植区/动物养殖区</h3>
#             <table class="market-table"><tr><td>名称</td><td>价格</td></tr>
#             市场每日 0/4/8/12/16/20 点固定刷新，波动 ±20%
#   - 仓库：<h2>仓库</h2> → <div class="warehouse-list">，空时 <p>暂无物品</p>；
#           有物品时为「批量出售表单 + .item_checkbox + 全选/取消全选 JS」
#   - 有效期：农作物 5 天、动物 5 天；农作物有 20% 概率双倍收获
import re
from typing import Dict, Optional, List, Any
from .base import FarmSiteConfig


class PtskitConfig(FarmSiteConfig):
    site_id = "ptskit"
    site_name = "拾刻(PTSKit)"
    domains = ["www.ptskit.org", "ptskit.org"]
    base_url = "https://www.ptskit.org"
    currency = "魔力"                       # 页面显示「当前魔力值」，确认
    farm_path = "/magic_farm.php"
    warehouse_path = "/magic_farm.php"      # 仓库同页（基类拼接 ?sort=expire_asc，页面支持该排序参数）
    has_double_harvest = True               # 农作物 20% 概率双倍收获

    # ===== 拾刻真实作物/动物（与基类默认一致，此处显式声明便于自文档化）=====
    crops: Dict[str, Dict] = {
        "crop_1":   {"name": "小麦", "cost": 500,    "type": "crop",   "id": 1},
        "crop_2":   {"name": "玉米", "cost": 1000,   "type": "crop",   "id": 2},
        "crop_3":   {"name": "花生", "cost": 1500,   "type": "crop",   "id": 3},
        "crop_4":   {"name": "土豆", "cost": 2000,   "type": "crop",   "id": 4},
        "animal_1": {"name": "鸡",   "cost": 1000,   "type": "animal", "id": 1},
        "animal_2": {"name": "猪",   "cost": 2000,   "type": "animal", "id": 2},
        "animal_3": {"name": "羊",   "cost": 5000,   "type": "animal", "id": 3},
        "animal_4": {"name": "牛",   "cost": 10000,  "type": "animal", "id": 4},
    }

    def parse_market_prices(self, html: str) -> Dict[str, int]:
        """
        拾刻菜市场：<h2>菜市场</h2> 区域内 <td>名称</td><td>价格</td>，
        农作物种植区与动物养殖区两张表都覆盖。
        """
        result: Dict[str, int] = {}
        name_to_key = self.get_name_to_key_map()

        market_start = html.find('<h2>菜市场</h2>')
        if market_start == -1:
            return result
        market_html = html[market_start:market_start + 8000]

        for name, price in re.findall(
            r'<td>([^<]+)</td>\s*<td>(\d+)</td>', market_html, re.DOTALL
        ):
            name = name.strip()
            if name in name_to_key and name not in result:
                result[name_to_key[name]] = int(price)
        return result

    def parse_crop_status(self, html: str) -> Dict[str, Dict]:
        """
        判断是否可收获：成熟后卡片按钮变为
        ?action=harvest&type=crop&id=N / ?action=harvest&type=animal&id=N（class="btn harvest-btn"）。
        生长中/空地显示的是 ?action=plant / ?action=breed，因此「出现 harvest 链接」即代表可收获。
        """
        result: Dict[str, Dict] = {}
        for key, crop in self.crops.items():
            can = rf'action=harvest&type={crop["type"]}&id={crop["id"]}' in html
            result[key] = {"can_harvest": can}
        return result

    def get_sell_key(self, html: str, item_type: str, item_id: int) -> Optional[str]:
        """
        出售 key：推测为 ?action=sell&key=类型_序号（如 crop_1 / animal_3），
        与主流程 fallback(f"{type}_{id}") 一致。
        ⚠️ 待验证：拾刻仓库页面带「批量出售表单 + .item_checkbox + 全选JS」，
        不排除出售需POST 勾选项(items[]/keys[])而非单个 sell 链接。
        请在仓库有实物时贴该页 HTML，我据此把出售逻辑改成对应的真实形式。
        """
        return f"{item_type}_{item_id}"

    def parse_warehouse_items(self, html: str) -> List[Dict[str, Any]]:
        """
        拾刻仓库：<h2>仓库</h2> → <div class="warehouse-list">，空时 <p>暂无物品</p>。
        有物品时为批量出售表单（.item_checkbox），行结构未实物确认，
        用容错写法：逐行优先找 action=sell&key=，否则取勾选框的 value 作为 key，
        名称/数量/过期时间就近从 <td> 取，不依赖固定列顺序。
        """
        items: List[Dict[str, Any]] = []
        warehouse_start = html.find('<h2>仓库</h2>')
        if warehouse_start == -1:
            return items
        warehouse_html = html[warehouse_start:warehouse_start + 10000]

        for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', warehouse_html, re.DOTALL):
            row = m.group(1)
            # 优先：单个出售链接
            sk = re.search(r'action=sell&key=([^"\'&\s]+)', row)
            if not sk:
                # 兜底：批量出售表单里的勾选框 value（items[]/keys[]/selected_items[]）
                cb = re.search(
                    r'<input[^>]*class=["\'][^"\']*item_checkbox[^"\']*["\'][^>]*value=["\']([^"\']+)["\']',
                    row, re.I)
                if not cb:
                    cb = re.search(
                        r'<input[^>]*name=["\'](?:items|keys|sell_keys|selected_items)\[\]["\'][^>]*value=["\']([^"\']+)["\']',
                        row, re.I)
                if not cb:
                    continue
                sell_key = cb.group(1).strip()
            else:
                sell_key = sk.group(1).strip()

            tds = [t.strip() for t in re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)]
            # 去掉纯 checkbox 的单元格
            tds = [t for t in tds if 'item_checkbox' not in t]
            name = ""
            for t in tds:
                clean = re.sub(r'<[^>]+>', '', t).strip()
                if clean and not clean.isdigit():
                    name = clean
                    break
            qty_m = re.search(r'<td[^>]*>\s*(\d+)\s*</td>', row, re.I)
            quantity = int(qty_m.group(1)) if qty_m else 1
            expire = ""
            for t in tds:
                clean = re.sub(r'<[^>]+>', '', t).strip()
                if re.search(r'\d{4}-\d{2}-\d{2}|\d+\s*(天|小时|分钟)', clean):
                    expire = clean
                    break
            items.append({
                "name": name,
                "quantity": quantity,
                "expire": expire,
                "sell_key": sell_key,
            })
        return items