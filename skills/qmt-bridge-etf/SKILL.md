---
name: qmt-bridge-etf
description: >-
  通过 QMT Bridge 查询 ETF 列表、申赎清单与相关行情，辅助 ETF 投资与套利观察。
  在用户提到 ETF、申赎、指数基金、ETF 套利时使用。只读。
---

# QMT Trading Skill · ETF

> **实现状态**：✅ `etf_snapshot.py` 可用

## 规划脚本

| 脚本 | 作用 |
|------|------|
| `scripts/etf_snapshot.py` | ETF 列表 + 指定 ETF info + tick |

## 主要 API

| 方法 | 路径 |
|------|------|
| GET | `/api/etf/list` |
| GET | `/api/etf/info` |
| GET | `/api/market/full_tick` |
| POST | `/api/download/etf_info` |

## 规程

- 只读观察；申赎/交易走 [qmt-bridge-trading](../qmt-bridge-trading/SKILL.md)
- 套利需用户自行定义阈值

## 参考

- ``qmt-bridge-next` 能力清单（`GET /capabilities`）`

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称**：由桥接公开行情源（腾讯/东方财富）
  提供，本 Skill 已可正常获取数据；公开源非官方接口，休市时段返回最近收盘数据。
- **本 Skill 依赖的其余数据**（板块成分 / 财务 / 公式引擎 / 列表类接口等）
  仍返回 **501 unsupported** 并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
