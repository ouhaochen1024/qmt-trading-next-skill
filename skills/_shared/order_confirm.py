"""订单确认追踪 —— 两阶段下单语义（qmt-bridge-next 信箱执行器）。

下单响应可能是 {"status":"submitted","tag":...,"order_id":0}：
order_id 提交时不可知，确认要靠 tag 追踪：

- 轮询 GET /api/trading/orders，按 order_remark == tag 匹配，直到
  order_id 非空（confirmed）或超时；
- 或订阅 WS /ws/order 收 order_confirmed / order_confirm_timeout
  （脚本场景默认用轮询，避免 asyncio 依赖）。

重要：超时按 order_confirm_timeout 处理 —— 报告"已提交但未确认，
请人工检查"，绝不重新下单（同一请求 id 在执行器侧幂等，人工重下
才是重复执行风险）。
"""

from __future__ import annotations

import time
from typing import Any


def find_order_by_tag(orders: list, tag: str) -> dict | None:
    for row in orders or []:
        if str(row.get("order_remark") or "") == tag:
            return row
    return None


def order_confirmed(row: dict | None) -> bool:
    """order_id 非空且非 0 即确认（信箱执行器语义）。"""
    if not row:
        return False
    oid = row.get("order_id")
    return oid not in (None, "", 0, "0")


def wait_for_confirmation(
    client,
    tag: str,
    *,
    account_id: str = "",
    timeout: float = 15.0,
    interval: float = 0.5,
) -> dict[str, Any] | None:
    """轮询委托列表直到 tag 对应订单确认；超时返回 None。

    返回值：
      - {"status":"confirmed","order": row}  已确认，order_id 可用
      - None                                  超时未确认（不要重下单）
    """
    if not tag:
        return None
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = client.query_orders(account_id=account_id)
        orders = resp.get("data") if isinstance(resp, dict) else resp
        row = find_order_by_tag(orders or [], tag)
        if order_confirmed(row):
            return {"status": "confirmed", "order": row}
        time.sleep(interval)
    return None
