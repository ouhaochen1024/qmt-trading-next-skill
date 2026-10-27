---
name: qmt-bridge-sector-theme
description: >-
  通过 QMT Bridge 做板块与主题研究：成分股、板块内涨跌排序、指数权重。
  在用户提到板块轮动、主题、行业强弱、成分股排名时使用。只读。
---

# QMT Trading Skill · 板块主题

> **实现状态**：⚠ 脚本就绪（`sector_rank.py`），后端 **501** 不可用

>
> **⚠ 本构建不可用**：本技能依赖 `/api/sector/*`，在 qmt-bridge-next 信箱版中一律返回
> **501 unsupported**（脚本会明确报错退出，不会返回假数据）。保留本技能是为了
> 契约与脚本不丢失；需要该能力请改用 miniQMT 版桥接，或等执行器后续覆盖。

## 目标

从**板块 → 成分 → 强弱排序**形成观察池，服务主题投资与行业比较框架。

## 脚本

| 脚本 | 作用 |
|------|------|
| `scripts/sector_rank.py` | `--list-sectors` 列出板块；`--sector` 排序 |

### 有效板块名

须以 `--list-sectors` 为准。实测常用：`沪深A股`、`上证A股`、`深证A股`、`创业板`、`科创板`。  
**注意**：`中证500` 等名称可能无效（返回空成分）。

### 性能

大板块默认仅扫描前 **800** 只成分（`--max-scan`）；可用 `--sample` 随机抽样。

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sector/list` | 板块列表 |
| GET | `/api/sector/stocks` | 成分股 |
| GET | `/api/sector/info` | 板块元数据 |
| GET | `/api/instrument/index_weight` | 指数权重 |
| GET | `/api/market/full_tick` | 成分行情 |

## 规程（规划）

1. `sector/list` 或用户指定板块名
2. `sector/stocks` 取成分
3. 批量 `full_tick`，按涨跌幅排序输出 Top N（含 `batch_stock_name` 中文名）
4. **仅观察池，不自动下单**

## 安全

- 只读

## 参考

- [qmt-bridge-market-watch](../qmt-bridge-market-watch/SKILL.md) · `qmt-bridge-next` 能力清单（`GET /capabilities`）

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称**：由桥接公开行情源（腾讯/东方财富）
  提供，本 Skill 已可正常获取数据；公开源非官方接口，休市时段返回最近收盘数据。
- **本 Skill 依赖的其余数据**（板块成分 / 财务 / 公式引擎 / 列表类接口等）
  仍返回 **501 unsupported** 并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
