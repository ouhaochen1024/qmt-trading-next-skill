---
name: qmt-bridge-convertible
description: >-
  通过 QMT Bridge 查询可转债列表与条款信息，辅助转债双低、强赎等策略观察。
  在用户提到可转债、转债、强赎、转股时使用。只读。
---

# QMT Trading Skill · 可转债

> **实现状态**：⚠ 脚本就绪（`cb_snapshot.py`），后端 **501** 不可用

>
> **⚠ 本构建不可用**：本技能依赖 `/api/cb/*`，在 qmt-bridge-next 信箱版中一律返回
> **501 unsupported**（脚本会明确报错退出，不会返回假数据）。保留本技能是为了
> 契约与脚本不丢失；需要该能力请改用 miniQMT 版桥接，或等执行器后续覆盖。

## 规划脚本

| 脚本 | 作用 |
|------|------|
| `scripts/cb_snapshot.py` | 转债列表 + 单券 info |

## 主要 API

| 方法 | 路径 |
|------|------|
| GET | `/api/cb/list` |
| GET | `/api/cb/info` |
| POST | `/api/download/cb_data` |

## 规程

- 只读；交易走 trading skill
- 强赎/下修等规则以 info 字段为准，Skill 不预测价格

## 参考

- `qmt-bridge-next` 能力清单（`GET /capabilities`）

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称**：由桥接公开行情源（腾讯/东方财富）
  提供，本 Skill 已可正常获取数据；公开源非官方接口，休市时段返回最近收盘数据。
- **本 Skill 依赖的其余数据**（板块成分 / 财务 / 公式引擎 / 列表类接口等）
  仍返回 **501 unsupported** 并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
