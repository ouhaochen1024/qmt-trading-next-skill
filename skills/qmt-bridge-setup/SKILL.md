---
name: qmt-bridge-setup
description: >-
  安装、配置并启动 QMT Bridge（qmt-bridge-next 信箱桥接），检查健康状态，并同步本仓客户端 .env。
  在用户提到安装 Bridge、启动桥接、Bridge 连不上、健康检查、
  配置信箱路径 / 账号 / API Key 时使用。不涉及下单。
---

# QMT Trading Skill · Bridge 安装与启动（qmt-bridge-next 信箱版）

> **实现状态**：✅ 规程可用；`bridge_health.py` 做连通性检查
>
> **架构**：大 QMT 客户端内置策略（信箱执行器）+ 外部 HTTP/WS 桥接进程。
> 不使用 miniQMT、不需要 xtquant、不需要「独立交易」登录。

## 目标

在 **Windows（与大 QMT 同机）** 部署 qmt-bridge-next，使本仓及其他 Agent Skills
能通过 HTTP 调用**交易与账户查询**接口（行情类能力见各 Skill 的「构建限制」说明）。

## 总规程（必须遵守）

1. **先健康检查**：运行 `bridge_health.py` 或请求 `GET /api/meta/health`
2. **服务已可达** → 向用户报告主机/端口与健康结果，**禁止**重复安装、禁止重启桥接（除非用户明确要求）
3. **服务不可达** → 再按下方「安装 → 启动 → 验证 → 同步本仓 `.env`」执行

## 提示词示例

| 场景 | 提示词 |
|------|--------|
| 推荐（先检测） | `检查 QMT Bridge 是否已启动；若未启动再帮我安装并启动。已在跑则不要重复安装或重启。` |
| 首次安装 | `帮我安装并启动 QMT Bridge（大 QMT 信箱桥接）` |
| 日常启动 | `启动 qmt-bridge-next` |
| 排障 | `Bridge 连不上，帮我做健康检查` · `/health 显示 degraded，帮我排查执行器` |
| 配置客户端连接 | `帮我配置 Skills 连接 QMT Bridge：主机 127.0.0.1，端口 8000，写入 skills 根 .env 后做健康检查（API Key 勿打进聊天）` |
| 配置服务端 | `配置桥接的端口、API Key、信箱路径和资金账号` |

## 前提条件

- **Windows** + **Python 3.10+**（桥接端）
- **大 QMT 客户端**已登录，策略「运行设置」里选择了交易账户（实盘或模拟均可）
- 本机或局域网防火墙放行 Bridge 端口（默认 `8000` / `.env` 中实际端口）

## 服务端部署（一次性）

### 1. 执行器进大 QMT（内部端）

1. 编辑 `<部署根>\config\config.ini`（唯一配置源，三端共用）：
   `account_id` / `base_dir` / `host` / `port` / `api_key`；
2. 运行盖戳脚本：`bash <部署根>\mailbox\stamp_executor.sh`（把 base_dir
   与 config.ini 绝对路径写进执行器常量 BASE_DIR / CONFIG_INI）
   （把 base_dir 写进执行器的 `BASE_DIR` 常量，幂等）；
3. 把盖戳后的 `qmt_mailbox_executor.py` 全文粘贴进 QMT 策略，
   运行周期 **1 秒**，运行设置里选择交易账户，重启；
4. 控制台确认 `build=2026-10-27-mbx10+`、`mailbox=<base_dir>`、
   `account id loaded from config.ini`；
5. 收紧信箱 ACL（必做）：
   `icacls "<base_dir>" /inheritance:r /grant:r "%USERNAME%:(OI)(CI)F"`

### 2. 桥接进程（外部端）

```powershell
cd qmt-bridge-next
pip install -e ".[dev]"
# 约定：QMT_BRIDGE_HOME 指向部署根（默认 D:\qmt-bridge-next），
# 全部产物收敛在 <HOME>\mailbox\ 内（in/out/bad、hello.json、agent.hb、
# account.ini、logs\、.env）。桥接按链读取配置：
#   cwd\.env → $QMT_BRIDGE_HOME\.env → <HOME>\mailbox\.env
set QMT_BRIDGE_HOME=D:\qmt-bridge-next
python -m qmt_bridge_next
```

## 规程：验证

**任何安装 / 启动操作之前与之后都应跑一次。**

```powershell
curl http://127.0.0.1:8000/api/meta/health

# 本仓脚本（读本仓 .env）
python skills/qmt-bridge-setup/scripts/bridge_health.py
python skills/qmt-bridge-setup/scripts/bridge_health.py --host 127.0.0.1 --port 8000
```

判定标准：

- `status=healthy` + `account_id` 非空 → 全链路就绪；
- `503 degraded` + `executor not alive` → 执行器未启动/信箱路径不一致：
  检查 QMT 策略是否在跑、`.env` 的 `QMT_BRIDGE_MAILBOX` 是否与执行器
  控制台 `paths resolved` 输出一致；
- `bound=false` → 账号未绑定：检查运行设置里的账户与 `account.ini`。

健康检查通过后再跑交易/复盘类 Skill。

## 规程：同步客户端 `.env`

配置写在 **Skills 安装根**（与 `_shared` 同级），不是某个单独的 `qmt-bridge-*` 目录内。

| 场景 | `.env` 位置 |
|------|-------------|
| 社区 / Agent 安装 | `<skills-root>/.env`（可先复制同级的 `.env.example`） |
| git 克隆本仓库 | 仓库根 `.env`（复制仓库根或 `skills/.env.example`） |

```powershell
# 在 skills 根（Agent 安装）或仓库根（开发克隆）
copy .env.example .env
```

必填项：`QMT_BRIDGE_HOST` / `QMT_BRIDGE_PORT` / `QMT_BRIDGE_API_KEY`，
可选 `QMT_BRIDGE_STOCK_ACCOUNT_ID`（与服务端 `account.ini` 一致）。
