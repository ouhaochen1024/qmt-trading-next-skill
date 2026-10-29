---
name: qmt-bridge-market-watch
description: >-
  通过 QMT Bridge 看盘：涨跌家数/赚钱效应、板块强弱、指数环境、自选快照、北向可得口径。
  在用户提到看盘、自选监控、盘前检查、行情快照、大盘环境、今天行情怎么样、复盘当日盘面时使用。只读，不下单。
---

# QMT Trading Skill · 自选监控 / 盘面速览

> **实现状态**：✅ `watchlist_snapshot.py`（自选+指数）· ✅ `market_summary.py`（盘面速览）

## 目标

回答两类问题，输出摘要（含中文名称）：

1. **自选池 + 大盘环境**：指定代码的涨跌幅、现价、指数背景；
2. **今日盘面速览**：涨跌家数（赚钱效应）、涨停跌停、两市成交额、
   行业/概念板块强弱、北向资金可得口径。

## 脚本

| 脚本 | 作用 |
|------|------|
| `scripts/market_summary.py` | 盘面速览：指数 + 涨跌家数 + 板块排行 + 北向；`--type hy/gn/dy`、`--top N`、`--json` |
| `scripts/watchlist_snapshot.py` | `--codes` 自选；`--indices-only` 仅指数 |

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/indices` | 主要指数 |
| GET | `/api/market/breadth` | **涨跌家数**：涨/跌/平、涨停/跌停、涨跌分布、两市成交额（亿元） |
| GET | `/api/sector/rank?type=hy` | **板块排行**：涨跌幅、主力净流入、板块内涨跌家数、领涨股 |
| GET | `/api/market/northbound` | **北向**：净额不可用，仅 T+1 成交总额 |
| GET | `/api/market/full_tick` | 实时快照（自选） |
| GET | `/api/market/market_data_ex` | K 线（可选） |
| GET | `/api/calendar/is_trading_date` | 交易日 |

## 规程

1. 校验交易日（可选，见 event-calendar）；
2. 要「今天行情怎么样」→ 跑 `market_summary.py`：一次拿齐指数、涨跌家数、
   板块强弱、北向；
3. 要「自选怎么样」→ `watchlist_snapshot.py --codes ...`；
4. 板块内部再看强弱 → [qmt-bridge-sector-theme](../qmt-bridge-sector-theme/SKILL.md)
   （`/api/sector/stocks?sector=煤炭`）；
5. **只输出观察结果，不推荐买卖**。

## 输出口径（重要，别编数字）

- **涨跌家数**：`up/down/flat`、`limit_up/limit_down`（±11% 桶 = 涨跌停）、
  `up_ge_5/down_le_minus5`、`up_ratio`（上涨占比 = 赚钱效应）；字段为
  `null` 表示该数据源无此统计，**不要当成 0**。
- **成交额**：`turnover_yi`（亿元，沪深两市合计）。
- **板块**：`pct_chg` 为板块涨跌幅；`main_net_inflow_wan` 是**万元**，
  转亿元要除以 10000；`up_count/down_count` 是板块内涨跌家数。
- **北向**：`available=false`、`net_inflow_yi=null` 是**正常**结果
  （2024-08-19 起交易所停止披露），只能引用 `north.turnover_yi`
  并说明「成交总额，不等于净买入」。**禁止**用成交额反推净流入。

## 安全

- 只读；行情端点默认无需 Key（若服务端开启数据鉴权则配置 Key）

## 参考

- `qmt-bridge-next` 能力清单（`GET /capabilities`） · [qmt-bridge-sector-theme](../qmt-bridge-sector-theme/SKILL.md)

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称 / 涨跌家数 / 板块 / 分笔**：由桥接
  公开行情源（腾讯 + 东方财富）提供，本 Skill 均已可用；公开源非官方接口，
  休市时段返回最近收盘数据，请求过频会被上游限流（桥接内置缓存与多源兜底）。
- **北向资金净买入**：交易所已停止披露，桥接如实返回 `available=false`。
- **财务 / 公式引擎 / ETF / 期权 / 两融标的**等仍返回 **501 unsupported**
  并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
