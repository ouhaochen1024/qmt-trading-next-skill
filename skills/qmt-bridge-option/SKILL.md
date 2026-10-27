---
name: qmt-bridge-option
description: >-
  通过 QMT Bridge 查询期权链、合约详情与列表，辅助期权策略与对冲分析。
  在用户提到期权、期权链、认沽认购、对冲时使用。只读。
---

# QMT Trading Skill · 期权

> **实现状态**：✅ `option_chain_snapshot.py` 可用

## 规划脚本

| 脚本 | 作用 |
|------|------|
| `scripts/option_chain_snapshot.py` | 标的 → 期权链摘要 |

## 主要 API

| 方法 | 路径 |
|------|------|
| GET | `/api/option/chain` |
| GET | `/api/option/detail` |
| GET | `/api/option/list` |
| GET | `/api/option/his_option_list` |

## 规程

- 只读；开仓/平仓若 API 支持须单独确认
- 希腊值/定价若 API 未提供，不在 Skill 内推算

## 参考

- ``qmt-bridge-next` 能力清单（`GET /capabilities`）`

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称**：由桥接公开行情源（腾讯/东方财富）
  提供，本 Skill 已可正常获取数据；公开源非官方接口，休市时段返回最近收盘数据。
- **本 Skill 依赖的其余数据**（板块成分 / 财务 / 公式引擎 / 列表类接口等）
  仍返回 **501 unsupported** 并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
