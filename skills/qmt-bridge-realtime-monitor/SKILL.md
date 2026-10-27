---
name: qmt-bridge-realtime-monitor
description: >-
  指导通过 QMT Bridge WebSocket 订阅实时行情、L2、公式推送与交易回报并对账。
  在用户提到 WebSocket 订阅、盘中推送、成交回报、实时盯盘时使用。规程为主。
---

# QMT Trading Skill · 实时监控

> **实现状态**：⚠ 事件通道可用（`/ws/order`、`/ws/events`）；**行情推送 WS 不可用**

>
> **⚠ 部分不可用**：本构建没有行情推送 WS —— `/ws/realtime`、`/ws/whole_quote`
> 等旧端点返回 **4501**；可用的只有 `/ws/order`（订单确认）与 `/ws/events`
> （执行器事件）。实时价格请用 `--codes` 轮询 `/api/market/full_tick`。

## 目标

规范 **WebSocket** 使用方式，避免 Agent 随意长连或泄露 Key。

## WebSocket 端点

| 路径 | 用途 | 认证 | 本构建 |
|------|------|------|--------|
| `/ws/events` | 执行器全量事件（order_*、async_response 等） | 无 | ✅ 可用 |
| `/ws/order` | 仅订单确认类事件 | 无 | ✅ 可用 |
| `/ws/realtime` | 实时行情推送 | 无 | ❌ 4501 |
| `/ws/whole_quote` | 全市场推送 | 无 | ❌ 4501 |
| `/ws/l2_thousand` | L2 千档 | 无 | ❌ 4501 |
| `/ws/formula` | 公式推送 | 无 | ❌ 4501 |
| `/ws/download_progress` | 下载进度 | 无 | ❌ 4501 |
| `/ws/trade` | 旧版交易回报 | `?api_key=` | ❌ 4501 |

行情轮询：`GET /api/market/full_tick?stocks=...`（本构建无行情推送）。

## 规程

1. 先 `GET /api/meta/health`；确认执行器存活再连 WS
2. 订单确认：连 `/ws/order` 后**再**下单；超时未收到 `order_confirmed`
   用 `GET /api/trading/orders` 对账（WS 只回放最近事件，不保证不丢）
3. 行情观察：轮询 `/api/market/full_tick`，在客户端聚合，**不**把全量
   tick/L2 dump 给 LLM
4. 断线重连：指数退避；记录最后 `seq`
5. 停止：关闭连接即可（无需 unsubscribe，本构建无订阅协议）

## 规划脚本（可选）

| 脚本 | 作用 |
|------|------|
| `scripts/ws_subscribe.py` | CLI 示例：订阅 codes 并打印摘要 N 秒 |

## 安全

- `/ws/trade` 的 api_key 勿写入日志
- 监控不等于自动下单

## 参考

- [qmt-bridge-technical-signal](../qmt-bridge-technical-signal/SKILL.md)
- [qmt-bridge-order-ops](../qmt-bridge-order-ops/SKILL.md)

## 数据来源与构建限制（qmt-bridge-next）

- **行情快照 / K 线 / 交易日历 / 股票名称**：由桥接公开行情源（腾讯/东方财富）
  提供，本 Skill 已可正常获取数据；公开源非官方接口，休市时段返回最近收盘数据。
- **本 Skill 依赖的其余数据**（板块成分 / 财务 / 公式引擎 / 列表类接口等）
  仍返回 **501 unsupported** 并明确报错——预期降级，不是故障。
- 能力清单见桥接端 `GET /capabilities` 与 `qmt-bridge-next/docs/limitations.md`。
