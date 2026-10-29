---
name: qmt-bridge-sector-theme
description: >-
  通过 QMT Bridge 做板块与主题研究：板块排行（涨跌幅/主力净流入）、成分股、板块内涨跌排序。
  在用户提到板块轮动、主题、行业强弱、板块排行、成分股排名时使用。只读。
---

# QMT Trading Skill · 板块主题

> **实现状态**：✅ 可用（`/api/sector/*` 已由腾讯板块源覆盖）

## 目标

从**板块 → 成分 → 强弱排序**形成观察池，服务主题投资与行业比较框架。

## 脚本

| 脚本 | 作用 |
|------|------|
| `scripts/sector_rank.py` | `--list-sectors` 列出板块；`--sector 煤炭` 排序 |

一次看全板块强弱，直接用盘面速览脚本的板块段落：
`qmt-bridge-market-watch/scripts/market_summary.py --type hy|gn|dy`

### 有效板块名

以 `--list-sectors` 为准。板块来自腾讯三套分类：

- **行业（hy，31 个）**：煤炭、银行、食品饮料、电子、通信、美容护理…
- **概念（gn，800+）**：证金持股、昨日连板、SpaceX概念、航天系…
- **地域（dy，31 个）**：青海、贵州、陕西…

**注意**：`沪深A股`、`上证50`、`中证500` 这类 xtdata 指数板块名**不适用**，
传了会返回 404（`unknown sector`）。

### 性能

板块接口已直接返回带行情的成分明细（`/api/sector/stocks`），
大板块无需再逐个 `full_tick`；旧脚本 `--max-scan` 仅作兜底。

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sector/list?type=hy` | 板块列表（`sectors` 名称 + `boards` 明细） |
| GET | `/api/sector/rank?type=hy&sort=pct_chg&limit=20` | 板块排行（本地排序：涨跌幅 / 主力净流入 / 换手 / 5·20·60 日） |
| GET | `/api/sector/stocks?sector=煤炭` | 成分股含行情（`stocks` 代码 + `items` 明细） |
| GET | `/api/sector_stocks?sector=煤炭` | legacy：仅成分代码 |
| GET | `/api/market/full_tick` | 成分行情（如需自定义批量） |

`main_net_inflow_wan` 单位**万元**（除 10000 得亿元）。

## 规程

1. `sector/rank` 看谁强谁弱（或用户指定板块）
2. `sector/stocks?sector=<名称>` 取成分含行情，按 `pct_chg` 排序
3. 输出 Top N / Bottom N（含中文名、涨跌幅、主力净流入）
4. **仅观察池，不自动下单**

## 安全

- 只读（自定义板块写操作仍 501）

## 参考

- [qmt-bridge-market-watch](../qmt-bridge-market-watch/SKILL.md) · `qmt-bridge-next` 能力清单（`GET /capabilities`）

## 数据来源与构建限制（qmt-bridge-next）

- **板块列表 / 排行 / 成分 / 个股行情**：腾讯公开板块接口，非 QMT 源；
  休市时段返回最近收盘数据，公开接口字段若变更需桥接端适配。
- **自定义板块写操作**（创建 / 增删成分 / 重置）仍返回 **501 unsupported**。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
