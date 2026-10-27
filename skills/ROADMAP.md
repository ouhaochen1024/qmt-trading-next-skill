# Skills 实现路线图

**QMT Trading Skill** 的 Agent Skills 层；底层 API 为 **QMT Bridge**。各 Skill 的 `SKILL.md` 与可执行脚本已对齐；共享模块见 [`_shared/`](_shared/)。

> **状态以 qmt-bridge-next 信箱版为准**：标 ⚠ 501 的技能，脚本完整、契约保留，
> 但依赖的路由组在信箱版返回 501 unsupported，需 miniQMT 版桥接才能用。

## 实现状态图例

| 标记 | 含义 |
|------|------|
| ✅ | 脚本可用，后端已覆盖 |
| ⚠ 501 | 脚本就绪，但依赖路由组在信箱版返回 501（本构建不可用） |
| ⚠ 4501 | 依赖的 WS 端点在信箱版返回 4501 |

## 全部 Skill 状态

| 优先级 | Skill | 状态 | 脚本 |
|--------|-------|------|------|
| P0 | [qmt-bridge-setup](qmt-bridge-setup/SKILL.md) | ✅ | 规程 + `bridge_health.py` |
| P0 | [qmt-bridge-trading](qmt-bridge-trading/SKILL.md) | ✅ | `trading_status.py`, `place_order.py`, `liquidate.py` |
| P0 | [qmt-bridge-execution-review](qmt-bridge-execution-review/SKILL.md) | ✅ | 证据包 + `daily_trade_report` / `combined_trade_report`；三角色专家规程 |
| P0 | [qmt-bridge-feishu-doc](qmt-bridge-feishu-doc/SKILL.md) | ✅ | 规程 + lark-cli（lark-doc / lark-drive） |
| P0 | [qmt-bridge-portfolio-risk](qmt-bridge-portfolio-risk/SKILL.md) | ✅ | `portfolio_snapshot.py` |
| P0 | [qmt-bridge-daily-pnl](qmt-bridge-daily-pnl/SKILL.md) | ✅ | `daily_pnl_snapshot.py` |
| P0 | [qmt-bridge-order-ops](qmt-bridge-order-ops/SKILL.md) | ✅ | `list_orders.py`, `cancel_orders.py` |
| P0 | [qmt-bridge-kline-backfill](qmt-bridge-kline-backfill/SKILL.md) | ✅ | `index_turnover_recent.py` · `backfill_recent_index_kline.py` |
| P1 | [qmt-bridge-return-analysis](qmt-bridge-return-analysis/SKILL.md) | ✅ | `return_probability_analysis.py` |
| P1 | [qmt-bridge-market-watch](qmt-bridge-market-watch/SKILL.md) | ✅ | `watchlist_snapshot.py` |
| P1 | [qmt-bridge-sector-theme](qmt-bridge-sector-theme/SKILL.md) | ⚠ 501 | `sector_rank.py` |
| P1 | [qmt-bridge-financial-download](qmt-bridge-financial-download/SKILL.md) | ⚠ 501 | `download_financial_data.py` |
| P1 | [qmt-bridge-fundamental-screen](qmt-bridge-fundamental-screen/SKILL.md) | ⚠ 501 | `screen_financial.py` |
| P1 | [qmt-bridge-technical-signal](qmt-bridge-technical-signal/SKILL.md) | ⚠ 501 | `formula_check.py` |
| P2 | [qmt-bridge-smart-execution](qmt-bridge-smart-execution/SKILL.md) | ✅ | `execution_preview.py` |
| P2 | [qmt-bridge-rebalance](qmt-bridge-rebalance/SKILL.md) | ✅ | `rebalance_plan.py` |
| P2 | [qmt-bridge-credit-margin](qmt-bridge-credit-margin/SKILL.md) | ⚠ 501 | `credit_snapshot.py` |
| P3 | [qmt-bridge-realtime-monitor](qmt-bridge-realtime-monitor/SKILL.md) | ⚠ 4501 | `ws_subscribe.py` + SKILL 规程 |
| P3 | [qmt-bridge-event-calendar](qmt-bridge-event-calendar/SKILL.md) | ✅ | `calendar_check.py` |
| P4 | [qmt-bridge-etf](qmt-bridge-etf/SKILL.md) | ⚠ 501 | `etf_snapshot.py`（按需） |
| P4 | [qmt-bridge-convertible](qmt-bridge-convertible/SKILL.md) | ⚠ 501 | `cb_snapshot.py`（按需） |
| P4 | [qmt-bridge-option](qmt-bridge-option/SKILL.md) | ⚠ 501 | `option_chain_snapshot.py`（按需） |
| P4 | [qmt-bridge-hk-connect](qmt-bridge-hk-connect/SKILL.md) | ⚠ 501 | `hk_universe.py`（按需） |

## 设计约束

- 研究类只读；写操作须 `--execute --confirm`
- 输出摘要，避免 dump 全量 JSON
- 不提供投资建议式结论
