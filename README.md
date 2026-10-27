# QMT Trading Skill (next)

> 用自然语言完成 A 股交易、持仓查询、当日盈亏、复盘与飞书同步。底层通过 **qmt-bridge-next** 对接大 QMT（无 xtquant / 无 miniQMT），三端共用一个 `config.ini`。

两个仓库各管一半，装的时候都要装：

| 仓库 | 装在哪 | 内容 |
|------|--------|------|
| **本仓库** qmt-trading-next-skill | Agent 的技能目录 | 23 个 Agent Skills（`SKILL.md` + 脚本 + `_shared` 共享库） |
| **[qmt-bridge-next](https://github.com/ouhaochen1024/qmt-bridge-next)** | 跑大 QMT 的 Windows 机器 | HTTP/WS 桥接 + 大 QMT 内部执行器 + 公开行情源 |

## 一键安装

前提：Windows（与大 QMT 同机）+ 大 QMT 已登录且账户可用 + Python 3.10+。

把下面整段粘进 Agent 对话（DeepSeek Harness / 豆包工作 / WorkBuddy / Cursor 均可）。它会按顺序装 Skill、装桥接、配好连接并自检；只有第 3 步贴执行器需要你亲自动手。

```text
帮我安装 QMT Trading Skill 全家桶（Skills + 桥接服务）。按顺序执行，每步做完汇报，需要我提供信息时先问我。

【第 1 步：安装 Skills】
来源：https://github.com/ouhaochen1024/qmt-trading-next-skill
1. 把 skills/ 下每个 qmt-bridge-* 目录装成独立 Skill（含 SKILL.md、scripts、references）。
2. 必须把 skills/_shared 复制到与这些 Skill 同一父目录（它没有 SKILL.md，不要注册成 Skill，
   但缺少它脚本会 ImportError）。
3. 一并复制 skills/VERSION，装完读出并告诉我版本号。
4. 仓库根其它文件不要装成 Skill。

【第 2 步：部署桥接服务】
1. 把 https://github.com/ouhaochen1024/qmt-bridge-next 克隆到与大 QMT 同机的 Windows 机器，
   默认 D:\qmt-bridge-next——装之前先问我路径。
2. 在该目录执行 pip install -e ".[dev]"。
3. 用 config/config.example.ini 生成 config/config.ini：
   host=127.0.0.1、port=8000、api_key 随机生成 32 位、base_dir 指向该仓库 mailbox 的绝对路径；
   account_id 先留空，然后问我要资金账号再填进去。
4. 执行 bash mailbox/stamp_executor.sh 盖戳。
5. 设置用户级环境变量 QMT_CONFIG 指向这份 config.ini 的绝对路径，确保 Skills 无论装在
   哪个目录都能找到配置（兄弟目录布局时它是可选的，但设了最稳）。

【第 3 步：需要我手工做，你只负责告诉我】
1. 把 mailbox/qmt_mailbox_executor.py 全文贴进大 QMT 策略编辑器，运行周期设为 1 秒，
   在"运行设置"里绑定交易账户，然后重启策略。
2. 提醒我核对执行器控制台三行：init begin build=...、paths resolved、account id loaded。

【第 4 步：启动并自检】
1. 后台启动 python -m qmt_bridge。
2. 运行 python <skills-root>/qmt-bridge-setup/scripts/bridge_health.py。
3. 汇报：Skills 版本、桥接是否 healthy、执行器是否 alive、account_id 是否绑定、还差哪些步骤。

约束：已在运行的桥接不要重复安装或重启；API Key 和账号不要打进对话；
下单、撤单、调仓等写操作必须我确认后再执行。
```

装完的目录长这样（父目录名各 Agent 不同，如 `~/.workbuddy/skills`、`.cursor/skills`）：

```text
<skills-root>/
├── VERSION
├── _shared/                # 共享库，必须有，但不是 Skill
├── qmt-bridge-setup/
├── qmt-bridge-trading/
└── …其它 qmt-bridge-*
```

> `_shared` 必须与各 Skill 同级——脚本用 `parents[2] / "_shared"` 找它，漏了就会 ImportError。

## 装好了吗：一次自检

```powershell
# 1) 连通性（不需要密钥）
python <skills-root>/qmt-bridge-setup/scripts/bridge_health.py
# 2) 配置与鉴权链路（读取 config.ini 的 api_key 并查账户）
python <skills-root>/qmt-bridge-trading/scripts/trading_status.py
```

或者在对话里说：`检查 QMT Bridge 是否已启动，并确认技能版本`。

四项都满足才算通：

1. `status=healthy`
2. `executor.alive=true`
3. `executor.account_id` 非空
4. `trading_status.py` 能打印账户与持仓（不报"未设置 API Key"或 401）

> `bridge_health.py` 故意跳过鉴权（`require_api_key=False`），只证明"能连上"；
> 配置与密钥是否正确，要靠 `trading_status.py` 这一步。

## 日常使用

直接说人话即可，不用记命令：

| 想做什么 | 这样说 | 状态 |
|----------|--------|------|
| 查持仓/资金 | `帮我查持仓和可用资金` | 可用 |
| 下单/撤单 | `买 000001.SZ 100 股限价 10.5` · `撤掉所有可撤委托` | 可用，需你确认 |
| 当日盈亏 | `今天账户盈亏多少` | 可用 |
| 行情快照 | `自选行情快照` · `今天是不是交易日` | 可用 |
| 复盘 | `用投顾/基金经理/交易员三角色做今日复盘并综合裁决` | 可用 |
| 涨幅概率 | `评估持仓涨幅概率并总结明日策略` | 可用 |
| 组合风控 | `组合风险快照，看下持仓集中度` | 可用 |
| 调仓 | `按目标权重生成调仓计划` | 可用（仅 JSON 权重） |
| 执行预览 | `预览这笔买单的冲击和资金占用` | 可用（无涨跌停校验） |
| 同步飞书 | `把今日复盘同步到飞书` | 可用（需 lark-cli 登录） |
| 板块 / 财务 / 公式 / ETF / 可转债 / 期权 / 港股通 / 两融 | 对应提问 | 501 降级：执行器未覆盖，会明确报错 |
| 实时行情推送 | — | 4501 不可用；看行情用快照轮询 |

降级不是故障，是桥接显式返回"不支持"。完整技能清单见 [skills/README.md](skills/README.md)，能力边界见 [limitations.md](https://github.com/ouhaochen1024/qmt-bridge-next/blob/main/docs/limitations.md) 与 [skills/ROADMAP.md](skills/ROADMAP.md)。

## 配置：只有一个文件

`qmt-bridge-next/config/config.ini`，桥接 / 执行器 / Skills 三端共用：

| 键 | 说明 |
|----|------|
| `host` / `port` | 桥接监听地址与端口（默认 `127.0.0.1:8000`；要局域网访问才改 `0.0.0.0`） |
| `api_key` | 交易与账户接口的密钥，Skills 请求头 `X-API-Key` 必须一致 |
| `account_id` | 普通资金账号（执行器启动时绑定） |
| `credit_account_id` / `default_account` | 信用账号 / 默认户，可选 |
| `base_dir` | 信箱目录，执行器与桥接必须指向同一处 |

Skills 会自动发现兄弟仓库的这份配置；装到 Agent 技能根、没有兄弟仓库时，用环境变量 `QMT_CONFIG` 指向它即可，无需额外文件。临时连别的桥接用 `--host/--port/--api-key` 覆盖。

手动部署（不走一键安装时）：

```bash
git clone https://github.com/ouhaochen1024/qmt-bridge-next.git
cd qmt-bridge-next && pip install -e ".[dev]"
cp config/config.example.ini config/config.ini   # 填 api_key / account_id / base_dir
bash mailbox/stamp_executor.sh                    # 盖戳后把执行器贴进 QMT
python -m qmt_bridge                              # 启动，日志在 mailbox/logs/
```

## 更新

对话里说：

```text
帮我把 qmt-trading-next-skill 更新到最新版：https://github.com/ouhaochen1024/qmt-trading-next-skill
覆盖安装时：1) 更新全部 qmt-bridge-*；2) 同步更新同级 _shared；3) 更新 VERSION 并告诉我版本号。
```

用 CLI 也可以：`npx skills update -g -y`（或 `npx skills add ouhaochen1024/qmt-trading-next-skill -g -y` 强制重装）。
更新后**新开一轮对话**，避免旧会话缓存旧规程。桥接有更新时，重新拉取仓库并重贴执行器。

## 排障

| 现象 | 先查什么 |
|------|----------|
| 脚本 `ImportError` / 找不到 module | `_shared` 没和各 Skill 放在同一级 |
| `连接失败` / `/health` 打不开 | 桥接进程是否在跑；端口是否与 `config.ini` 一致 |
| 报 `HTTP 502: upstream connect failed` | 本机装了代理（Clash/V2Ray 等）时会劫持 `127.0.0.1` 请求：先确认桥接在跑，再用 `curl --noproxy '*'` 或关闭代理验证 |
| `503 degraded` + `executor not alive` | QMT 策略是否在运行；`base_dir` 与 `config.ini` 是否一致 |
| `401 invalid or missing API key` | 请求头 key 与 `config.ini` 的 `api_key` 不一致 |
| `403 order writes disabled` | 桥接启动时带了 `QMT_BRIDGE_ORDER_WRITES_DISABLED=1` |
| 返回 `501 unsupported` | 该能力本构建未覆盖，属预期降级，不是故障 |

## 开发

- 改 Skill：递增 `skills/VERSION` 并在 [`skills/CHANGELOG.md`](skills/CHANGELOG.md) 记一行。
- 改桥接：见 [qmt-bridge-next](https://github.com/ouhaochen1024/qmt-bridge-next)，`pytest tests/` 跑 22 项测试。

## 许可

MIT（本仓库暂未附 `LICENSE` 文件；对外分发前请补 MIT 全文与版权归属）
