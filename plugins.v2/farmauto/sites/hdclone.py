# sites/hdclone.py - HDClone 站点配置
# 适配说明：HDClone 使用【定制版】NexusPHP 农场页面（magic_farm.php），
# 与 PlayLet/NovaHD/好学/包子 那套标准 magic_farm 插件结构不同：
#   - 作物/动物卡片：<div class="farm-item"><h3>名称</h3><p>价格: X</p>
#                       <a href="?action=plant&type=crop&id=N"> / ?action=breed&type=animal&id=N
#   - 菜市场：<h2>菜市场</h2> 内含 <div class="market-category"><h3>农作物种植区/动物养殖区</h3>
#                       <table class="market-table"><tr><td>名称</td><td>市场价格</td></tr>
#   - 仓库：<h2>仓库</h2>（同页），有物品时为 <table class="warehouse-table"> 行
#   - 成熟后收获链接应为 ?action=harvest&type=crop&id=N（与基类 get_harvest_url 一致）
# 注意：HDClone 实际作物/动物清单、成本与基类默认（4+4）完全不同，已在此完整覆盖。
import re
from typing import Dict, Optional, List, Any
from .base import FarmSiteConfig


class HdCloneConfig(FarmSiteConfig):
    site_id = "hdclone"
    site_name = "HDClone"
    domains = ["pt.hdclone.top"]
    base_url = "https://pt.hdclone.top"
    currency = "魔力"                  # 页面显示「当前魔力值」，确认
    farm_path = "/magic_farm.php"
    warehouse_path = "/magic_farm.php"  # 仓库同页（?sort=expire_asc 由基类拼接，页面会忽略该参数）

    # ===== HDClone 真实作物/动物清单（来自 magic_farm.php，8 作物 + 8 动物）=====
    # cost 取卡片上的「价格: X」（种植/养殖消耗的魔力值）
    crops: Dict[str, Dict] = {
        "crop_1":   {"name": "小麦", "cost": 5000,   "type": "crop",   "id": 1},
        "crop_2":   {"name": "玉米", "cost": 10000,  "type": "crop",   "id": 2},
        "crop_3":   {"name": "花生", "cost": 15000,  "type": "crop",   "id": 3},
        "crop_4":   {"name": "土豆", "cost": 20000,  "type": "crop",   "id": 4},
        "crop_5":   {"name": "甘蔗", "cost": 20000,  "type": "crop",   "id": 5},
        "crop_6":   {"name": "椰子", "cost": 30000,  "type": "crop",   "id": 6},
        "crop_7":   {"name": "菠萝", "cost": 40000,  "type": "crop",   "id": 7},
        "crop_8":   {"name": "榴莲", "cost": 50000,  "type": "crop",   "id": 8},
        "animal_1": {"name": "鸡",   "cost": 70000,  "type": "animal", "id": 1},
        "animal_2": {"name": "狗",   "cost": 80000,  "type": "animal", "id": 2},
        "animal_3": {"name": "牛",   "cost": 90000,  "type": "animal", "id": 3},
        "animal_4": {"name": "虎",   "cost": 100000, "type": "animal", "id": 4},
        "animal_5": {"name": "龟",   "cost": 110000, "type": "animal", "id": 5},
        "animal_6": {"name": "鹤",   "cost": 120000, "type": "animal", "id": 6},
        "animal_7": {"name": "凤",   "cost": 130000, "type": "animal", "id": 7},
        "animal_8": {"name": "龙",   "cost": 200000, "type": "animal", "id": 8},
    }

    def parse_market_prices(self, html: str) -> Dict[str, int]:
        """
        HDClone 菜市场：<h2>菜市场</h2> 区域内 <td>名称</td><td>市场价格</td>。
        直接在菜市场区域用通用 <td>名称</td><td>价格</td> 解析（作物+动物两类都覆盖）。
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
        判断是否可收获：成熟后页面出现收获链接
        ?action=harvest&type=crop&id=N（与基类 get_harvest_url 一致）。
        空农场/生长中不会出现该链接 → can_harvest=False。
        """
        result: Dict[str, Dict] = {}
        for key, crop in self.crops.items():
            can = rf'action=harvest&type={crop["type"]}&id={crop["id"]}' in html
            result[key] = {"can_harvest": can}
        return result

    def get_sell_key(self, html: str, item_type: str, item_id: int) -> Optional[str]:
        """
        出售 key：HDClone 出售链接推测为 ?action=sell&key=类型_序号（如 crop_1 / animal_3）。
        与主流程 fallback（f"{type}_{id}"）一致。
        ⚠️ 待验证：若 HDClone 实际 sell key 带后缀/哈希（如 crop_1_169...），
        请贴仓库页 HTML，我在此用正则重写。
        """
        return f"{item_type}_{item_id}"

    def parse_warehouse_items(self, html: str) -> List[Dict[str, Any]]:
        """
        HDClone 仓库：<h2>仓库</h2> 有物品时为 <table class="warehouse-table"> 行。
        行结构未实物确认（当前为空仓库），用「逐行找出售链接 + 就近取名称/数量」的容错写法，
        不依赖固定列顺序。
        """
        items: List[Dict[str, Any]] = []
        warehouse_start = html.find('<h2>仓库</h2>')
        if warehouse_start == -1:
            return items
        warehouse_html = html[warehouse_start:warehouse_start + 10000]

        for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', warehouse_html, re.DOTALL):
            row = m.group(1)
            sk = re.search(r'action=sell&key=([^"\'&\s]+)', row)
            if not sk:
                continue
            tds = re.findall(r'<td>([^<]*)</td>', row)
            name = tds[0].strip() if len(tds) >= 1 else ""
            qty_m = re.search(r'<td>(\d+)</td>', row)
            quantity = int(qty_m.group(1)) if qty_m else 1
            expire = tds[2].strip() if len(tds) >= 3 else ""
            items.append({
                "name": name,
                "quantity": quantity,
                "expire": expire,
                "sell_key": sk.group(1).strip(),
            })
        return items
