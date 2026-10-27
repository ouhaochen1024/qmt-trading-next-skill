---
name: qmt-bridge-event-calendar
description: >-
  通过 QMT Bridge 查询交易日历、节假日、交易时段，并支持用户自定义的财报/持仓事件检查规程。
  在用户提到是否交易日、节假日、交易时间、财报日、日历时使用。只读。
---

# QMT Trading Skill · 事件日历

> **实现状态**：✅ `calendar_check.py` 可用

## 目标

交易与风控的**时间上下文**：是否可交易、下一交易日、用户自定义规则检查。

## 规划脚本

| 脚本 | 作用 |
|------|------|
| `scripts/calendar_check.py` | 今日是否交易日、上下交易日、当前是否在交易时段 |

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/calendar/is_trading_date` | 是否交易日 |
| GET | `/api/calendar/trading_dates` | 交易日列表 |
| GET | `/api/calendar/holidays` | 节假日 |
| GET | `/api/calendar/trading_period` | 交易时段 |
| GET | `/api/calendar/prev_trading_date` | 上一交易日 |
| GET | `/api/calendar/next_trading_date` | 下一交易日 |
| GET | `/api/meta/last_trade_date` | 最近交易日 |

## 规程（规划）

1. 输出日历结论（是/否交易日、时段）
2. **用户规则**（如「财报前一日减仓」）写在配置/对话，脚本只执行布尔检查并提示，不自动下单
3. 可与 [portfolio-risk](../qmt-bridge-portfolio-risk/SKILL.md) 联动

## 安全

- 只读

## 参考

- ``qmt-bridge-next` 能力清单（`GET /capabilities`）`

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称**：由桥接公开行情源（腾讯/东方财富）
  提供，本 Skill 已可正常获取数据；公开源非官方接口，休市时段返回最近收盘数据。
- **本 Skill 依赖的其余数据**（板块成分 / 财务 / 公式引擎 / 列表类接口等）
  仍返回 **501 unsupported** 并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
