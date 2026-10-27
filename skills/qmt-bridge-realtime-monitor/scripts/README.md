# qmt-bridge-realtime-monitor 脚本

| 脚本 | 状态 | 说明 |
|------|------|------|
| `ws_subscribe.py` | ✅ 可用 | 事件 WS 监听（`/ws/events` 或 `/ws/order`）+ 行情轮询（`--codes`） |

主文档见上级 `SKILL.md`。注意：本构建**没有行情推送 WS**（`/ws/realtime` 等返回 4501），
实时价走 `GET /api/market/full_tick` 轮询。
