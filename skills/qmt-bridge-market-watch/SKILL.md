---
name: qmt-bridge-market-watch
description: >-
  通过 QMT Bridge 对自选标的做行情快照：涨跌幅、现价、指数环境、交易日校验。
  在用户提到看盘、自选监控、盘前检查、行情快照、大盘环境时使用。只读，不下单。
---

# QMT Trading Skill · 自选监控

> **实现状态**：✅ `watchlist_snapshot.py`

## 目标

盘前/盘中/盘后快速浏览**自选池**与**大盘环境**，输出表格摘要（含中文名称）。

## 脚本

| 脚本 | 作用 |
|------|------|
| `scripts/watchlist_snapshot.py` | `--codes` 自选；`--indices-only` 仅指数 |

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/full_tick` | 实时快照 |
| GET | `/api/market/indices` | 主要指数 |
| GET | `/api/market/market_data_ex` | K 线（可选） |
| GET | `/api/calendar/is_trading_date` | 交易日 |

## 规程（规划）

1. 校验交易日（可选，见 event-calendar）
2. 拉 `indices` 作为环境背景（或 `--indices-only` 快速看盘）
3. 对 `--codes` 批量 `full_tick`，输出涨跌幅等
4. **只输出观察结果，不推荐买卖**

## 安全

- 只读；行情端点默认无需 Key（若服务端开启数据鉴权则配置 Key）

## 参考

- `qmt-bridge-next` 能力清单（`GET /capabilities`） · [qmt-bridge-sector-theme](../qmt-bridge-sector-theme/SKILL.md)

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称**：由桥接公开行情源（腾讯/东方财富）
  提供，本 Skill 已可正常获取数据；公开源非官方接口，休市时段返回最近收盘数据。
- **本 Skill 依赖的其余数据**（板块成分 / 财务 / 公式引擎 / 列表类接口等）
  仍返回 **501 unsupported** 并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
