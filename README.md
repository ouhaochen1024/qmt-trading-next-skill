# QMT Trading Skill (next)

> 在 Cursor / Claude Code / **DeepSeek Harness** / **豆包工作** / **WorkBuddy** 中用**自然语言**完成交易、当日盈亏、复盘与飞书同步。底层通过 **qmt-bridge-next**（大 QMT 内置策略 + 文件信箱桥接，无 xtquant / 无 miniQMT）对接大 QMT。
>
> **迁移说明**：本仓库由 qmt-trading-skill 迁移而来，各 Skill 的对话契约（SKILL.md 触发词、角色、报告格式）保持不变；变化仅在底层：HTTP 客户端已 vendor 进 `skills/_shared/qmb_vendor`，下单改为两阶段语义（submitted + tag 追踪），配置统一读取 `qmt-bridge-next/config/config.ini`（唯一配置源）。

本仓库只含 **Agent Skills**（`skills/`）。HTTP/WS API 与信箱执行器在平级仓库 **[ouhaochen1024/qmt-bridge-next](https://github.com/ouhaochen1024/qmt-bridge-next)**（`mailbox/` 为大 QMT 内部端，桥接包为 `qmt_bridge/`）。

**仓库内文档**：[快速开始](#一键安装) · [Agent Skills](skills/README.md) · [能力与限制（桥接）](https://github.com/ouhaochen1024/qmt-bridge-next/blob/main/docs/limitations.md)

## 一键安装

在 **DeepSeek Harness**、**豆包工作**、**WorkBuddy** 等 Agent 的对话里直接粘贴下面提示词，Agent 会自动拉取并安装本仓库的 Skills。

```text
帮我安装这个 skill：https://github.com/ouhaochen1024/qmt-trading-next-skill

安装布局（必须遵守）：
1. 把 skills/ 下每个 qmt-bridge-* 目录安装为独立 Skill（含 SKILL.md、scripts、references）。
2. 同时把 skills/_shared 复制到与上述 Skill 同一父目录下（与各 qmt-bridge-* 并列）。
   _shared 是共享库、没有 SKILL.md，不要注册成 Skill，但必须复制，否则脚本会 ImportError。
3. 一并复制 skills/VERSION（便于核对版本）。
4. 不要把仓库根目录其它文件误装成 Skill。

安装完成后：读取 VERSION；说明如何用自然语言查持仓、当日盈亏和生成复盘；
并确认 _shared 已与各 Skill 同级存在。
```

正确目录示例（父目录名因 Agent 而异，如 `~/.agents/skills`、`~/.workbuddy/skills`、`.cursor/skills`）：

```text
<skills-root>/
├── VERSION                 # 包版本
├── _shared/                # 共享库（必须有，不是 Skill）
├── qmt-bridge-setup/
├── qmt-bridge-trading/
├── qmt-bridge-execution-review/
└── …其它 qmt-bridge-*
```

脚本用 `Path(__file__).parents[2] / "_shared"` 定位共享模块，因此 **`_shared` 必须与各 Skill 目录同级**。仅安装 `qmt-bridge-*`、漏拷 `_shared` 时，从技能目录跑脚本会失败。

> **安装后连接配置**：Skills 会自动发现兄弟仓库 `qmt-bridge-next/config/config.ini`（开发克隆布局）。若按上表安装到 Agent 技能根（无兄弟仓库），设置环境变量 **`QMT_CONFIG`** 指向 Bridge 部署根的统一配置文件（`qmt-bridge-next/config/config.ini`）即可，Skills 会自动把其中的 `host` / `port` / `api_key` / `account_id` / `credit_account_id` / `default_account` 映射为连接参数，无需任何额外配置文件。

### 通用 CLI（可选）

任意支持 [Agent Skills](https://skills.sh/) 的环境也可用：

```bash
npx skills add ouhaochen1024/qmt-trading-next-skill -g -y
```

CLI 按仓库结构安装时一般会带上同仓文件；若本地只有分散的 Skill 目录，请按上面布局补齐 `_shared`。

安装 Skills 后，下一步是检测 / 按需启动 Bridge（见下方「使用」第 2 步），不要默认重复安装或重启已在跑的服务。

## 版本

| 项 | 位置 | 当前 |
|----|------|------|
| Skills 包版本 | [`skills/VERSION`](skills/VERSION) | 以文件内容为准 |
| 变更说明 | [`skills/CHANGELOG.md`](skills/CHANGELOG.md) | 按版本记录 |

发版约定：改 Skill 行为或新增 Skill 时递增 `skills/VERSION`，并在 `CHANGELOG.md` 写一行。Agent 更新后应能读到新的 `VERSION` 内容。

## 更新 Skills（已安装用户）

仓库有新版本时，**已安装**本 Skill 包的 Agent 需主动拉取覆盖，不会自动升级。

### 对话一键更新（DeepSeek Harness / 豆包工作 / WorkBuddy / Cursor 等）

```text
帮我把 qmt-trading-next-skill 更新到最新版：https://github.com/ouhaochen1024/qmt-trading-next-skill

覆盖安装时保持布局：
1. 更新全部 qmt-bridge-* Skill 目录；
2. 同步更新同级的 _shared（共享库，不注册为 Skill，但必须存在）；
3. 更新 VERSION，读出并告诉我版本号。
```

若 Agent 使用 `npx skills`，也可说：`用 npx skills update 更新 ouhaochen1024/qmt-trading-next-skill，并核对 VERSION`。

### 通用 CLI

```bash
# 检查是否有更新
npx skills check

# 更新全部已装 Skill（全局安装用 -g）
npx skills update -g -y

# 或强制重装本仓库（覆盖）
npx skills add ouhaochen1024/qmt-trading-next-skill -g -y
```

### 开发克隆（git）

```powershell
git clone https://github.com/ouhaochen1024/qmt-trading-next-skill.git
cd qmt-trading-next-skill
Get-Content skills\VERSION
```

更新后**新开一轮对话**再触发 Skill，避免旧会话缓存旧规程。若本地改过某 Skill 文件，覆盖前请自行备份。

## 仓库职责

| 仓库 | 内容 | 说明 |
|------|------|------|
| **[ouhaochen1024/qmt-bridge-next](https://github.com/ouhaochen1024/qmt-bridge-next)** | 大 QMT 信箱执行器（`mailbox/`）、HTTP/WS 桥接（`qmt_bridge/`）、公开行情源、统一配置 | 实盘验收通过：下单→柜台确认→撤单 |
| **本仓库** | `skills/`、复盘调度、Skill 文档 | 只含 Agent Skills，通过 HTTP/WS 访问桥接 |

典型用法：在 Windows（与大 QMT 同机）部署执行器并启动 Bridge → 在 Agent / 本仓跑 Skills。配置统一在一个文件：

- **`qmt-bridge-next/config/config.ini`（唯一配置源，三端共用）**：`host` / `port` / `api_key` / `account_id` / `base_dir`
- **执行器**：修改 base_dir/账号后跑一次 `mailbox/stamp_executor.sh` 盖戳并重贴 QMT
- **Skills（客户端）**：自动发现兄弟仓库的 `config/config.ini`（或 `QMT_CONFIG` 显式指定），通常**零配置**；命令行参数可临时覆盖

## 配置客户端连接

各 Skill 脚本通过 HTTP 访问已启动的 Bridge，**不会自动发现端口**。连接参数统一由 [`skills/_shared/common.py`](skills/_shared/common.py) 解析。

**优先级（高 → 低）：** 命令行 `--host` / `--port` / `--api-key` → 进程环境变量 → **统一配置 `config\config.ini`** → 默认值（`127.0.0.1` / `8000`）。

### 统一配置（唯一配置源）

Skills 会自动查找兄弟仓库 `qmt-bridge-next/config/config.ini`（也可用环境变量 `QMT_CONFIG` 显式指定路径），把以下键映射为连接参数：

| config.ini 键 | 映射 | 说明 |
|------|------|------|
| `host` | `QMT_BRIDGE_HOST` | 客户端目标，用 `127.0.0.1` 或局域网 IP |
| `port` | `QMT_BRIDGE_PORT` | 与 Bridge 实际监听端口一致（默认 `8000`） |
| `api_key` | `QMT_BRIDGE_API_KEY` | 与 Bridge 一致；交易/持仓类必填 |
| `account_id` | `QMT_BRIDGE_STOCK_ACCOUNT_ID` | 普通资金账号（可选） |
| `credit_account_id` | `QMT_BRIDGE_CREDIT_ACCOUNT_ID` | 信用两融账号（可选） |
| `default_account` | `QMT_BRIDGE_DEFAULT_ACCOUNT` | 默认户 `stock` / `credit`（默认 `stock`） |

模板见 [`qmt-bridge-next/config/config.example.ini`](https://github.com/ouhaochen1024/qmt-bridge-next/blob/main/config/config.example.ini)；`config.ini` 本体已被 gitignore，真实账号/密钥不入库。

### 验证

```powershell
python <skills-root>/qmt-bridge-setup/scripts/bridge_health.py
# 或显式指定
python .../bridge_health.py --host 127.0.0.1 --port 8000
```

也可在对话中直接说（会走 [qmt-bridge-setup](skills/qmt-bridge-setup/SKILL.md)）：

```text
检查 QMT Bridge 是否已启动；若未启动再帮我安装并启动。已在跑则不要重复安装或重启。
```

Agent 规程要点：先健康检查 → 已可达则只报告状态 → 不可达再按 setup Skill 部署（执行器贴 QMT + 盖戳 + 启动桥接）→ 确认 host/port 实际生效值。

## 使用

### 1. 安装本仓库全部 Skills

先把本仓 `skills/` 下全部 Agent Skills 装进当前 Agent（跳过 `_shared`）。任选一种方式：

- **对话一键安装**（DeepSeek Harness / 豆包工作 / WorkBuddy）：见上方「一键安装」提示词
- **CLI**：`npx skills add ouhaochen1024/qmt-trading-next-skill -g -y`
- **开发克隆**：`git clone https://github.com/ouhaochen1024/qmt-trading-next-skill.git`

### 2. 检测并（按需）部署 QMT Bridge

Skills 装好后，在对话中说：

```text
检查 QMT Bridge 是否已启动；若未启动再帮我安装并启动。已在跑则不要重复安装或重启。
```

或 `@skills/qmt-bridge-setup/SKILL.md`。完整部署规程见该 SKILL.md（执行器贴 QMT → `config/config.ini` → 盖戳 → 启动桥接）。

> **Bridge 本体从哪来？** Bridge 服务端不在本仓库，来自 **[ouhaochen1024/qmt-bridge-next](https://github.com/ouhaochen1024/qmt-bridge-next)**。首次部署时在对话里直接说上面的提示词，Agent 会按 setup Skill 规程自动拉取该仓库到大 QMT 同机的部署根并完成部署；也可手动克隆：
>
> ```bash
> git clone https://github.com/ouhaochen1024/qmt-bridge-next.git
> ```
>
> 后续的配置（`config/config.ini`）、盖戳、执行器贴 QMT、启动桥接均由 setup Skill 按 SKILL.md 执行。

连不上时优先核对：桥接进程是否在跑、执行器策略是否在 QMT 里运行（`/health` 会给出 `executor not alive` 等明确原因）。

### 3. 开始使用

对话中直接说自然语言即可（也可 `@skills/.../SKILL.md`）。每个 Skill 一条典型提示词：

| Skill | 提示词 | 当前可用性 |
|-------|--------|-----------|
| [setup](skills/qmt-bridge-setup/SKILL.md) | `检查 QMT Bridge 是否已启动；若未启动再帮我安装并启动` | ✅ |
| [trading](skills/qmt-bridge-trading/SKILL.md) | `帮我查持仓和可用资金` / `买 000001.SZ 100 股限价 10.5` | ✅ 实盘验收通过 |
| [order-ops](skills/qmt-bridge-order-ops/SKILL.md) | `查今日委托和可撤单` / `撤掉所有可撤委托` | ✅ |
| [portfolio-risk](skills/qmt-bridge-portfolio-risk/SKILL.md) | `组合风险快照，看下持仓集中度` | ✅ |
| [daily-pnl](skills/qmt-bridge-daily-pnl/SKILL.md) | `今天账户盈亏多少` | ✅ |
| [market-watch](skills/qmt-bridge-market-watch/SKILL.md) | `自选行情快照` | ✅ 公开行情源 |
| [event-calendar](skills/qmt-bridge-event-calendar/SKILL.md) | `今天是不是交易日` | ✅ |
| [return-analysis](skills/qmt-bridge-return-analysis/SKILL.md) | `评估持仓涨幅概率并总结明日策略` | ✅ 公开行情源 |
| [execution-review](skills/qmt-bridge-execution-review/SKILL.md) | `用投顾/基金经理/交易员三角色做今日复盘并综合裁决` | ✅（行情部分走公开源） |
| [feishu-doc](skills/qmt-bridge-feishu-doc/SKILL.md) | `把今日复盘同步到飞书` | ✅ |
| [rebalance](skills/qmt-bridge-rebalance/SKILL.md) | `按目标权重生成调仓计划` | ✅ |
| [smart-execution](skills/qmt-bridge-smart-execution/SKILL.md) | `预览这笔买单会不会涨跌停` | ✅ |
| [sector-theme](skills/qmt-bridge-sector-theme/SKILL.md) | `今天行业强弱怎么排` | ⏸ 501 降级（板块接口未覆盖） |
| [financial-download](skills/qmt-bridge-financial-download/SKILL.md) | `下载财报到 Bridge 缓存` | ⏸ 501 降级 |
| [fundamental-screen](skills/qmt-bridge-fundamental-screen/SKILL.md) | `按 ROE、EPS 做基本面筛选` | ⏸ 501 降级 |
| [technical-signal](skills/qmt-bridge-technical-signal/SKILL.md) | `用 QMT 公式检查是否金叉` | ⏸ 501 降级 |
| [convertible](skills/qmt-bridge-convertible/SKILL.md) | `可转债列表和条款快照` | ⏸ 501 降级 |
| [etf](skills/qmt-bridge-etf/SKILL.md) | `查 ETF 列表和申赎清单` | ⏸ 501 降级 |
| [option](skills/qmt-bridge-option/SKILL.md) | `查 510050 期权链` | ⏸ 501 降级 |
| [hk-connect](skills/qmt-bridge-hk-connect/SKILL.md) | `港股通标的有哪些` | ⏸ 501 降级 |
| [credit-margin](skills/qmt-bridge-credit-margin/SKILL.md) | `查两融保证金和担保品` | ⏸ 501 降级 |
| [realtime-monitor](skills/qmt-bridge-realtime-monitor/SKILL.md) | `WebSocket 订阅实时行情` | ⏸ 501 降级 |

⏸ 501 降级 = 桥接显式返回"不支持"并说明原因（不是故障）；能力边界见 [qmt-bridge-next/docs/limitations.md](https://github.com/ouhaochen1024/qmt-bridge-next/blob/main/docs/limitations.md)。更多变体见 [skills/README.md](skills/README.md)。写操作（下单、撤单、调仓等）须你确认后再执行。

## 开发

- **本仓库**：改 Skill 后递增 `skills/VERSION` 并在 CHANGELOG 记录。
- **桥接**：见 [qmt-bridge-next](https://github.com/ouhaochen1024/qmt-bridge-next)（`python -m qmt_bridge` 启动；`pytest tests/` 跑 22 项测试）。

## 许可

MIT（本仓库暂未附 `LICENSE` 文件；对外分发前请补 MIT 全文与版权归属）
