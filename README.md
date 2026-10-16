# MoviePilot 插件仓库（个人维护版）

个人自用的 [MoviePilot](https://github.com/jxxghp/MoviePilot) 插件仓库，收录 3 个插件：**群聊区**、**农场自动化**、**PT自动任务助手**。

可直接作为 MoviePilot 的**自定义插件仓库**使用。

---

## 插件一览

| 插件 | 名称 | 版本 | 代码目录 | 登记于 | 作者 |
|---|---|---|---|---|---|
| GroupChatZone | 群聊区 | 2.3.4 | `plugins/groupchatzone/` | 根 `package.json` | yyzhou94, KoWming, madrays |
| FarmAuto | 农场自动化 | 1.4 | `plugins.v2/farmauto/` | `package.v2.json` | bfjy, yyzhou94 |
| PTAutoTasker | PT自动任务助手 | 1.5.0 | `plugins.v2/ptautotasker/` | `package.v2.json` | tmzg0000, yyzhou94 |

> ⚠️ **PTAutoTasker 是 v2 插件**，需要 MoviePilot `system_version >= 2.0.0, < 3.0.0`。

---

## 在 MoviePilot 中启用

### 方式 A：自定义插件仓库（推荐）
1. MoviePilot → **设置 → 插件 → 插件仓库**，填入：
   ```
   https://github.com/yyzhou94/MoviePilot-Plugins
   ```
2. 回到 **插件** 页面，点右上角 **刷新/更新插件库**（这一步不能省，否则拉不到新代码）
3. 找到目标插件，点 **安装/更新**

### 方式 B：手动放置
把插件目录（如 `plugins.v2/ptautotasker/`）整个复制到 MoviePilot 的插件目录，重启 MoviePilot。

---

## 各插件说明

### 1. 群聊区（GroupChatZone）v2.3.4
执行站点**喊话**、获取反馈、定时任务，支持 FlareSolverr 绕过 Cloudflare。

**相对上游改动**：`plugins/groupchatzone/__init__.py` 的 `target_site_names` 白名单追加 **「库非」**（`kufei.org`，标准 NexusPHP 站，通用 `NexusPHPHandler` 即可处理，无需新增 handler）。

**配置库非喊话**：
1. 站点管理添加库非（`https://kufei.org/index.php`，带有效 Cookie）
2. 插件配置：`选择站点` 勾选 **库非**；`自定义消息` 填一行：
   ```
   库非|库非福利求上传
   ```
   多条/自定义间隔：`库非|库非福利求上传|第二条|60s`
3. 点【立即运行一次】测试

> ⚠️ 站点名三处必须一致：站点管理里的名字 = 白名单里的名字 = 自定义消息行首的名字。

---

### 2. 农场自动化（FarmAuto）v1.4
适配多个站点的魔法农场，支持自动收获与智能交易。

**支持站点**：PlayLet、NovaHD、好学、包子、HDClone、**拾刻(PTSKit)**

**相对上游改动**：
- 新增 **拾刻（PTSKit，`www.ptskit.org`）**：农场页 `magic_farm.php`，货币=魔力，农作物 20% 概率双倍收获
- 新增 **HDClone（`pt.hdclone.top`）**：定制版 `magic_farm.php`，作物/动物与默认不同，已按其 16 项（8 作物 + 8 动物）单独适配
- 网络层优化（见下方「网络与超时」章节）

> 注意：HDClone 与拾刻的**出售 key 格式**按 `crop_1`/`animal_N` 兜底假设，若出售失败请反馈对应仓库页 HTML。

---

### 3. PT自动任务助手（PTAutoTasker）v1.5.0
PT 站点**任务领取 / 福利兑换 / 游戏 / 自动刮奖**助手，支持 18 个站点共 23 个任务。

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

**相对上游改动（1.2.9 ~ 1.5.0）**：全部集中在**网络与超时**优化，详见下方章节。躺平抽奖批量由 100 降为 25。

---

## 网络与超时（重点排查区）

三个插件都在**跨境/高延迟线路**下运行（实测部分 PT 站首包可达 15 秒）。本仓库统一做了以下优化：

### 已做的优化
| 优化 | 作用 |
|---|---|
| **连接复用** | 全局 `Session` + `HTTPAdapter` 连接池，同一站点多次请求只握手一次，省掉高延迟下每请求的 TCP+TLS 往返 |
| **分阶段超时** | 拆成「连接超时」与「读取超时」，连接慢快速失败，不白等读取预算 |
| **自动重试** | 瞬时故障（读取超时 / 连接重置 / DNS 临时失败 / 5xx）自动重试 2 次，退避递增；**4xx 不重试** |
| **友好错误提示** | 日志区分「连接超时 / 读取超时 / DNS 解析失败 / 连接被拒 / SSL 失败」，不再只丢一串原始堆栈 |

### 当前超时配置
| 插件 | 范围 | 连接 | 读取 |
|---|---|---|---|
| **PTAutoTasker** | 全局默认（17 站） | 10s | 30s |
| | 躺平抽奖（每批 25 次） | 10s | 60s |
| | 躺平老虎机 / Vc-Lib | 10s | 30s |
| **FarmAuto** | 全部农场请求 | 10s | 30s |
| **GroupChatZone** | 通用 NexusPHP | **3.05s** | 10s |

> ⚠️ **GroupChatZone 的连接超时 3.05 秒是全仓最短短板**。PT 站普遍套 Cloudflare，从国内握手超 3 秒就失败。若群聊区频繁超时，建议改`sites/__init__.py` 里的 `timeout=(3.05, 10)` 为 `(10, 30)`。

### 常见报错对照
| 日志关键字 | 含义 | 建议 |
|---|---|---|
| `Read timed out` | 连上了但服务器迟迟不返回数据 | 线路慢，加长读取超时或降低单批数量 |
| `ConnectTimeout` | TCP/TLS 握手都没完成 | 出口线路问题，可尝试走代理 |
| `Temporary failure in name resolution` | DNS 临时故障 | 已内置重试；仍失败则该域名可能已失效 |
| `认领人数已达上限` / `有其他进行中的任务` | 站点侧限制 | **正常**，非故障 |

### 进一步优化（宿主网络层面，需自行操作）
1. **启用 BBR** —— 高延迟国际链路提速最明显。CentOS 7 需先装 `elrepo` 的 `kernel-lt` 并重启
2. **DNS 调优** —— 对比不同 DNS 解析出的 IP，挑选首包最低的
3. **代理线路** —— PT 站走代理要权衡延迟与 **IP 干净度**（PT 站普遍 ban 机房 IP）

---

## 目录结构

```
MoviePilot-Plugins/
├── package.json                      # v1 插件清单（GroupChatZone）
├── package.v2.json                   # v2 插件清单（FarmAuto、PTAutoTasker）
├── plugins/
│   └── groupchatzone/                # 群聊区
└── plugins.v2/
    ├── farmauto/                     # 农场自动化
    │   └── net_util.py               # 网络层封装（连接池/超时/重试/错误提示）
    └── ptautotasker/                 # PT自动任务助手
        └── utils/
            ├── config.py             # 超时/重试配置
            └── custom_requests.py    # 网络层封装（连接池/超时/重试）
```

---

## 更新日志摘要

### FarmAuto
- **v1.4** 网络层优化（连接复用/分阶段超时/重试/友好错误提示）
- **v1.3** 农场请求超时 15s → 30s
- **v1.2** 新增拾刻（PTSKit）站点

### PTAutoTasker
- **v1.5.0** 网络层优化；躺平抽奖批量 100 → 25（单请求耗时降至 1/4）
- **v1.4.0** 全局超时 10s → 30s，躺平抽奖 60s → 120s
- **v1.3.0** 躺平抽奖单独放宽超时
- **v1.2.9** 全局超时 5s → 10s

### GroupChatZone
- **v2.3.4** 新增库非喊话功能

---

## 致谢

- **GroupChatZone** — 上游：[KoWming/MoviePilot-Plugins](https://github.com/KoWming/MoviePilot-Plugins)
- **FarmAuto** — 上游作者 bfjy
- **PTAutoTasker** — 上游：[tmzg0000/MoviePilot-Plugins](https://github.com/tmzg0000/MoviePilot-Plugins)（原作者 tmzg0000，基于 PTAutoTask / liuyunfz 演进）

本仓库仅存放个人自用版本，如有问题欢迎反馈。