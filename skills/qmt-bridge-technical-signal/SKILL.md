---
name: qmt-bridge-technical-signal
description: >-
  通过 QMT Bridge 调用 QMT 公式/指标，对单只或多只股票做技术信号检查。
  在用户提到技术指标、公式、MA、MACD、信号确认、QMT 指标时使用。只读。
---

# QMT Trading Skill · 技术信号

> **实现状态**：⚠ 脚本就绪（`formula_check.py`），后端 **501** 不可用

>
> **⚠ 本构建不可用**：本技能依赖 `/api/formula/*`，在 qmt-bridge-next 信箱版中一律返回
> **501 unsupported**（脚本会明确报错退出，不会返回假数据）。保留本技能是为了
> 契约与脚本不丢失；需要该能力请改用 miniQMT 版桥接，或等执行器后续覆盖。

## 目标

把已在 **QMT 中验证的公式**固化为可重复检查，避免 Agent 临时编造指标逻辑。

## 规划脚本

| 脚本 | 作用 |
|------|------|
| `scripts/formula_check.py` | `--formula` `--codes` 调用 `formula/call_batch` |

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/formula/call` | 单股公式 |
| POST | `/api/formula/call_batch` | 批量公式 |
| GET | `/api/formula/list` | 公式列表 |
| GET | `/api/market/market_data_ex` | K 线（备用） |
| WS | `/ws/formula` | 盘中公式推送（见 realtime-monitor） |

## 规程（规划）

1. `formula/list` 确认公式名存在
2. `call_batch` 对代码列表求值
3. 输出：代码 + 信号值/最后一根 K 线结论（由公式定义）
4. **信号 ≠ 下单指令**；交易须走 trading / smart-execution

## 安全

- 只读（公式调用不写交易）

## 参考

- `qmt-bridge-next` 能力清单（`GET /capabilities`） · [qmt-bridge-realtime-monitor](../qmt-bridge-realtime-monitor/SKILL.md)

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称**：由桥接公开行情源（腾讯/东方财富）
  提供，本 Skill 已可正常获取数据；公开源非官方接口，休市时段返回最近收盘数据。
- **本 Skill 依赖的其余数据**（板块成分 / 财务 / 公式引擎 / 列表类接口等）
  仍返回 **501 unsupported** 并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
