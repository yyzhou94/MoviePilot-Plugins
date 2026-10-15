# MoviePilot 插件仓库（个人维护版）

个人自用的 [MoviePilot](https://github.com/jxxghp/MoviePilot) 插件仓库，收录了 3 个插件（群聊区、农场自动化、PT自动任务助手）。

可直接作为 MoviePilot 的**自定义插件仓库**使用。

---

## 插件一览

| 插件 | 名称 | 版本 | 代码目录 | 登记于 | 作者 |
|---|---|---|---|---|---|
| GroupChatZone | 群聊区 | 2.3.4 | `plugins/groupchatzone/` | 根 `package.json` | yyzhou94, KoWming, madrays |
| FarmAuto | 农场自动化 | 1.1 | `plugins.v2/farmauto/` | `package.v2.json` | bfjy, yyzhou94 |
| PTAutoTasker | PT自动任务助手 | 1.3.0 | `plugins.v2/ptautotasker/` | `package.v2.json` | tmzg0000, yyzhou94 |

---

## 在 MoviePilot 中启用

### 方式 A：作为自定义插件仓库（推荐）
1. MoviePilot → 设置 → 插件 → 「自定义插件仓库」填入：
   ```
   https://github.com/yyzhou94/MoviePilot-Plugins
   ```
2. 重载插件列表，即可看到并安装上面的插件。

### 方式 B：手动放置
把对应插件目录（如 `plugins.v2/ptautotasker/`）整个复制到 MoviePilot 的插件目录，重启 MoviePilot。

---

## 各插件说明

### 1. 群聊区（GroupChatZone）v2.3.4
执行站点**喊话**、获取反馈、定时任务，支持 FlareSolverr 绕过 Cloudflare。

**相对上游改动**：在 `plugins/groupchatzone/__init__.py` 的 `target_site_names` 白名单追加了 **「库非」**（`kufei.org`）。
> 库非是标准 NexusPHP 站点，通用 `NexusPHPHandler` 即可处理，无需新增 handler 文件。

**配置库非喊话**：
1. 站点管理添加库非站点（`https://kufei.org/index.php`，带有效 Cookie）。
2. 插件配置：`选择站点` 勾选 **库非**；`自定义消息` 填一行：
   ```
   库非|库非福利求上传
   ```
   多条/自定义间隔：`库非|库非福利求上传|第二条|60s`
3. 点【立即运行一次】测试。

> ⚠️ 站点名三处必须一致：站点管理里的名字 = 白名单里的名字 = 自定义消息行首的名字。

---

### 2. 农场自动化（FarmAuto）v1.1
适配多个站点的魔法农场，支持自动收获与智能交易。

**支持站点**：PlayLet、NovaHD、好学、包子、**HDClone**。

**相对上游改动**：新增 **HDClone**（`pt.hdclone.top`）农场支持。
- HDClone 是定制版农场页（`magic_farm.php`），作物/动物与默认不同，已按其 16 项（8 作物 + 8 动物）单独适配。

> 注意：HDClone 的出售 key 格式按 `crop_1`/`animal_N` 兜底假设，若出售失败请反馈。

---

### 3. PT自动任务助手（PTAutoTasker）v1.3.0
PT 站点**任务领取 / 福利兑换 / 游戏 / 自动刮奖**助手，支持 18 个站点共 23 个任务。

> ⚠️ 本插件为 **v2 插件**，需要 MoviePilot `system_version >= 2.0.0, < 3.0.0`。

**支持站点 / 任务**：

| 站点 | 任务 |
|---|---|
| 藏宝阁 / 蟹黄堡 / 财神 / Ptskit | 任务领取 |
| 13City | 每日做种、每月做种 |
| 自由农场 | 每周任务领取 |
| HDVIDEO | 自动刮奖 |
| 垃圾堆 / LongPT / NovaHD | 每月任务 / 每月保种 |
| 柠檬 | 每日神游 |
| LuckPT | 勋章奖励（每日幸运星 +1000） |
| 青蛙 | 每日 1k 蝌蚪 |
| 躺平 | 任务领取、每日 1000 次抽奖、每日 2 次老虎机 |
| 象站 | 打 Boss |
| 织梦 | 勋章奖励 |
| CARPT / Vc-Lib | 任务领取 / 每周上传 + 每周魔力值 |

**相对上游改动（1.2.9 / 1.3.0）**：
- 修复站点请求默认**超时过短**：全局 `REQUEST_TIMEOUT` 由 `5` 秒 → **`10`** 秒（PT 站常因 Cloudflare + DB 查询超过 5s 导致 `Read timed out`）。
- 躺平**抽奖请求单独放宽至 60 秒**（单次请求服务端连抽最多 100 次，耗时较长）；老虎机保持 10 秒。

---

## 目录结构

```
MoviePilot-Plugins/
├── package.json                 # v1 插件清单（GroupChatZone）
├── package.v2.json              # v2 插件清单（FarmAuto、PTAutoTasker）
├── plugins/
│   └── groupchatzone/           # 群聊区
└── plugins.v2/
    ├── farmauto/                # 农场自动化
    └── ptautotasker/            # PT自动任务助手
```

---

## 致谢

- **GroupChatZone** — 上游：[KoWming/MoviePilot-Plugins](https://github.com/KoWming/MoviePilot-Plugins)
- **FarmAuto** — 上游作者 bfjy
- **PTAutoTasker** — 上游：[tmzg0000/MoviePilot-Plugins](https://github.com/tmzg0000/MoviePilot-Plugins)（原作者 tmzg0000，基于 PTAutoTask / liuyunfz 演进）

本仓库仅存放个人自用版本，如有问题欢迎反馈。