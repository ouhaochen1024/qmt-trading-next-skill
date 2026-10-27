#!/usr/bin/env python3
"""连接 qmt-bridge-next 的事件 WebSocket，并可选轮询行情快照。

本构建（信箱版）只提供两条 WS：
  /ws/events  全部执行器事件（**默认**）
  /ws/order   仅订单确认类事件（order_confirmed / timeout / async_response）

**没有**行情推送 WS（xtdata 订阅未覆盖）；要看实时价，用 `--codes` 走
`GET /api/market/full_tick` 轮询。旧的 /ws/realtime 会返回 4501。

用法:
    python skills/qmt-bridge-realtime-monitor/scripts/ws_subscribe.py --seconds 10
    python skills/qmt-bridge-realtime-monitor/scripts/ws_subscribe.py \\
        --channel order --codes 000001.SZ --seconds 10 --poll 3
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from common import (  # noqa: E402
    add_client_args,
    load_config,
    make_client,
    resolve_connection,
)

CHANNELS = ("events", "order")


async def _listen(url: str, seconds: int, label: str, samples: list) -> int:
    import websockets

    count = 0
    async with websockets.connect(url) as ws:
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=max(1, seconds))
                count += 1
                if len(samples) < 3:
                    try:
                        samples.append(json.loads(msg))
                    except json.JSONDecodeError:
                        samples.append({"raw": msg[:200]})
        except asyncio.TimeoutError:
            pass
    return count


async def _poll(client, codes: list[str], seconds: int, poll_sec: int) -> dict:
    """轮询行情快照（本构建没有行情推送 WS）。"""
    snapshots: dict[str, float] = {}
    elapsed = 0
    while elapsed < seconds:
        try:
            raw = await asyncio.to_thread(client.get_full_tick, codes)
            tick_map = raw.get("data", raw) if isinstance(raw, dict) else {}
            for code in codes:
                tick = tick_map.get(code) or tick_map.get(code.upper()) or {}
                price = tick.get("lastPrice")
                if price:
                    snapshots[code] = float(price)
        except Exception as exc:
            print(f"行情轮询失败: {type(exc).__name__}: {exc}", file=sys.stderr)
            break
        await asyncio.sleep(poll_sec)
        elapsed += poll_sec
    return snapshots


async def _run(host: str, port: int, channel: str, codes: list[str],
               seconds: int, poll_sec: int, client) -> int:
    try:
        import websockets  # noqa: F401
    except ImportError:
        print("错误: 需要 pip install websockets", file=sys.stderr)
        return 2

    url = f"ws://{host}:{port}/ws/{channel}"
    samples: list = []

    tasks = [
        asyncio.create_task(_listen(url, seconds, channel, samples)),
    ]
    if codes:
        tasks.append(asyncio.create_task(_poll(client, codes, seconds, poll_sec)))

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        for task in tasks:
            task.cancel()

    for item in results:
        if isinstance(item, Exception):
            code = None
            rcvd = getattr(item, "rcvd", None)
            if rcvd is not None:
                code = getattr(rcvd, "code", None)
            if code == 4501:
                print("错误: 该 WS 端点在本构建不支持（服务器返回 4501）。")
                print("可用端点: /ws/events（全部事件）、/ws/order（订单确认）；"
                      "行情请用 --codes 轮询 full_tick。")
                return 2
            print(f"WS 错误: {type(item).__name__}: {item}", file=sys.stderr)
            return 1

    received = results[0] if results and isinstance(results[0], int) else 0
    print(f"=== WebSocket 摘要 ({seconds}s) ===")
    print(f"  地址: {url}")
    print(f"  收到事件: {received} 条")
    if samples:
        text = json.dumps(samples[-1], ensure_ascii=False, default=str)
        print(f"  样本: {text[:300]}{'...' if len(text) > 300 else ''}")
    if len(results) > 1 and isinstance(results[1], dict) and results[1]:
        print("  行情轮询快照:")
        for code, price in results[1].items():
            print(f"    {code}: {price}")
    elif codes:
        print("  行情轮询: 未取到价格（检查 codes 与行情源）")
    return 0


def main() -> int:
    load_config()
    parser = argparse.ArgumentParser(
        description="事件 WebSocket 监听 + 行情轮询（本构建无行情推送 WS）"
    )
    add_client_args(parser)
    parser.add_argument(
        "--channel", choices=CHANNELS, default="events",
        help="events=全部执行器事件（默认），order=仅订单确认",
    )
    parser.add_argument("--codes", default="", help="可选：要轮询的代码，逗号分隔")
    parser.add_argument(
        "--seconds", "--duration", type=int, default=10,
        help="运行秒数（默认 10；演示脚本，非生产监控）",
    )
    parser.add_argument("--poll", type=int, default=3, help="行情轮询间隔秒（默认 3）")
    parser.add_argument("--period", default="tick",
                        help="已废弃：本构建无行情推送 WS，保留仅为兼容旧命令")
    args = parser.parse_args()

    host, port, _, _, _ = resolve_connection(args)
    codes = [c.strip() for c in args.codes.split(",") if c.strip()]
    client, _ = make_client(args, require_api_key=False)
    return asyncio.run(_run(host, port, args.channel, codes, args.seconds,
                            max(1, args.poll), client))


if __name__ == "__main__":
    sys.exit(main())
