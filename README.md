# groupchatzone（群聊区）插件 · 个人维护版

MoviePilot 插件 **群聊区（groupchatzone）**，用于执行站点喊话、获取反馈、定时任务。

- 上游来源：[KoWming/MoviePilot-Plugins](https://github.com/KoWming/MoviePilot-Plugins)（`plugins/groupchatzone`）
- 本仓库为**仅含该插件的独立仓库**，目录结构与原仓库保持一致（`plugins/groupchatzone/`），可直接作为 MoviePilot 的「自定义插件仓库」使用。

## 本仓库相对上游的改动

仅一处改动（`plugins/groupchatzone/__init__.py` 的 `get_form()` 内 `target_site_names` 白名单追加了 `"库非"`）：

```python
target_site_names = ["大青虫", "青蛙", "织梦", "象站", "幸运", "藏宝阁","天枢","好学", "Moment", "RailgunPT", "PTLGS", "LongPT", "LuckPT","13City","PTS", "库非"]
```

`库非`(kufei.org) 为标准 NexusPHP 站点，通用 `NexusPHPHandler` 即可处理，**无需新增 handler 文件**。

## 在 MoviePilot 中启用

两种方式任选其一：

### 方式 A：作为自定义插件仓库（推荐）
1. 在 GitHub 上把这个仓库设为 **Public**（或 MoviePilot 能访问的 Private）。
2. MoviePilot → 设置 → 插件 → 「自定义插件仓库」填入本仓库地址（如 `https://github.com/<你的用户名>/MoviePilot-Plugins`）。
3. 重载/安装插件即可，目录结构 `plugins/groupchatzone/` 会被自动识别。

### 方式 B：手动放置
把 `plugins/groupchatzone/` 整个目录复制到 MoviePilot 的插件目录下，重启 MoviePilot。

## 配置「库非」喊话

1. **站点管理**：在 MoviePilot 中添加库非站点（地址 `https://kufei.org/index.php`，带有效 Cookie）。
2. **群聊区插件配置**：
   - `选择站点`：勾选 **库非**
   - `自定义消息`：填一行
     ```
     库非|库非福利求上传
     ```
   - （可选）多条/自定义间隔：`库非|库非福利求上传|库非福利求上传2|60s`
3. 先点一次 **【立即运行一次】** 测试，确认喊话正常、不会重复刷屏。

> ⚠️ 站点名三处必须一致：MoviePilot「站点管理」里的名字 = `__init__.py` 白名单里的名字 = `自定义消息` 行首的名字（此处统一为「库非」）。

## 目录结构

```
plugins/groupchatzone/
├── __init__.py        # 插件主入口（已加入「库非」白名单）
├── form.py            # 配置页面定义
└── sites/             # 各站点喊话处理器（自动发现，无需注册）
    ├── __init__.py    # 抽象基类 ISiteHandler
    ├── NexusPHP.py    # 通用 NexusPHP 处理器（库非走这里）
    ├── 13City.py  Cangbao.py  Dubhe.py  Hxpt.py  LongPT.py
    ├── Luckpt.py  Moment.py   Ptlgs.py   Ptskit.py  Qingwa.py
    └── Vicomo.py  Zm.py
```

## 后续新增站点

若需再加其它标准 NexusPHP 站：把站点名加进 `__init__.py` 的 `target_site_names` 即可，无需写 handler。
若站点 shoutbox 接口非标（如 LongPT/青蛙/织梦等已有专属 handler），在 `sites/` 下新建 `Xxx.py` 继承 `NexusPHPHandler` 或 `ISiteHandler`，放进目录即被自动加载。
