#!/usr/bin/env python3
"""A 股盘面速览：指数 + 涨跌家数 + 板块排行 + 北向（只读）。

一次性回答「今天大 A 怎么样」：指数涨跌、赚钱效应（涨跌家数 / 涨停跌停 /
两市成交额）、行业或概念板块强弱、北向资金可得口径。

用法:
    python skills/qmt-bridge-market-watch/scripts/market_summary.py
    python skills/qmt-bridge-market-watch/scripts/market_summary.py --type gn --top 8
    python skills/qmt-bridge-market-watch/scripts/market_summary.py --json

北向说明：净买入自 2024-08-19 起停止披露，脚本只报 T+1 成交总额，
不做任何估算。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SHARED = Path(__file__).resolve().parents[2] / "_shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

from common import (  # noqa: E402
    add_client_args,
    call_api,
    fmt_num,
    load_config,
    make_client,
)

INDEX_NAMES = {
    "000001.SH": "上证指数",
    "399001.SZ": "深证成指",
    "399006.SZ": "创业板指",
    "000300.SH": "沪深300",
}


def _pct_from_tick(tick: dict) -> float:
    last = float(tick.get("lastPrice") or 0)
    prev = float(tick.get("lastClose") or tick.get("lastClosed") or 0)
    return round(((last - prev) / prev * 100) if prev else 0.0, 2)


def _indices(client) -> list[dict]:
    resp = call_api(client.get_major_indices)
    codes = resp.get("indices") or []
    ticks = resp.get("data") or {}
    rows = []
    for code in codes:
        t = ticks.get(code) or {}
        rows.append({
            "code": code,
            "name": INDEX_NAMES.get(code) or t.get("stockName") or code,
            "last": t.get("lastPrice"),
            "pct_chg": _pct_from_tick(t) if t else None,
        })
    return rows


def _board_row(b: dict) -> dict:
    lead = b.get("leader") or {}
    inflow = b.get("main_net_inflow_wan")
    return {
        "name": b.get("name"),
        "pct_chg": b.get("pct_chg"),
        "main_net_inflow_yi": round(inflow / 10000, 2) if inflow is not None else None,
        "up_count": b.get("up_count"),
        "down_count": b.get("down_count"),
        "leader": lead.get("name"),
        "leader_pct": lead.get("pct_chg"),
    }


def main() -> int:
    load_config()
    parser = argparse.ArgumentParser(description="A 股盘面速览（只读）")
    add_client_args(parser)
    parser.add_argument("--type", default="hy", choices=["hy", "gn", "dy"],
                        help="板块类型：hy 行业（默认）/ gn 概念 / dy 地域")
    parser.add_argument("--top", type=int, default=5, help="涨跌幅各输出前 N 名")
    parser.add_argument("--min-member", type=int, default=0,
                        help="板块成分股下限，过滤迷你概念板块（如 10）")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    client, _ = make_client(args, require_api_key=False)

    indices = _indices(client)
    breadth = call_api(client.get_market_breadth)
    rank = call_api(client.get_sector_rank, args.type, "pct_chg", "desc",
                    200, args.min_member)
    items = rank.get("items") or []
    north = call_api(client.get_northbound)

    top = [_board_row(b) for b in items[: args.top]]
    bottom = [_board_row(b) for b in list(reversed(items))[: args.top]]
    north_net = north.get("north") or {}

    payload = {
        "date": breadth.get("date"),
        "indices": indices,
        "breadth": {k: breadth.get(k) for k in (
            "up", "down", "flat", "limit_up", "limit_down", "up_ge_5",
            "down_le_minus5", "up_ratio", "net_advances", "turnover_yi",
            "source")},
        "sector_type": args.type,
        "sector_top": top,
        "sector_bottom": bottom,
        "north": {
            "available": north.get("available"),
            "net_inflow_yi": north.get("net_inflow_yi"),
            "turnover_date": north.get("date"),
            "turnover_yi": north_net.get("turnover_yi"),
            "note": north.get("note"),
        },
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return 0

    print("=== A 股盘面速览（%s）===" % (breadth.get("date") or "-"))
    print("指数: " + " | ".join(
        "%s %s %s%%" % (r["name"], fmt_num(r["last"]),
                        "%.2f" % r["pct_chg"] if r["pct_chg"] is not None else "-")
        for r in indices[:4]
    ))

    def _n(key: str) -> str:
        val = breadth.get(key)
        return "-" if val is None else str(val)

    print("涨跌家数: 涨 %s / 跌 %s / 平 %s（上涨占比 %s%%），涨停 %s / 跌停 %s"
          % (_n("up"), _n("down"), _n("flat"),
             "%.1f" % (breadth["up_ratio"] * 100) if breadth.get("up_ratio") is not None else "-",
             _n("limit_up"), _n("limit_down")))
    print("涨跌>5%%: 涨超5%% %s 家 / 跌超5%% %s 家" % (_n("up_ge_5"), _n("down_le_minus5")))
    turnover = breadth.get("turnover_yi")
    print("两市成交额: %s 亿" % (fmt_num(turnover) if turnover is not None else "-"))
    print("数据源: %s" % (breadth.get("source") or "-"))

    label = {"hy": "行业", "gn": "概念", "dy": "地域"}[args.type]

    def _line(r: dict) -> str:
        return ("  %-10s %+6.2f%%  主力 %s亿  涨跌 %s/%s  领涨 %s %s"
                % (r["name"] or "-", r["pct_chg"] or 0.0,
                   fmt_num(r["main_net_inflow_yi"]),
                   r["up_count"] if r["up_count"] is not None else "-",
                   r["down_count"] if r["down_count"] is not None else "-",
                   r["leader"] or "-",
                   ("%+.2f%%" % r["leader_pct"]) if r["leader_pct"] is not None else "-"))

    print("\n--- %s板块 涨幅前 %d（共 %d 个）---" % (label, len(top), rank.get("count") or 0))
    for r in top:
        print(_line(r))
    if bottom:
        print("--- %s板块 跌幅前 %d ---" % (label, len(bottom)))
        for r in reversed(bottom):
            print(_line(r))

    print("\n--- 北向资金 ---")
    if not north.get("available"):
        print("净买入: 不可用（%s）" % (north.get("note") or "上游停止披露"))
    if north_net.get("turnover_yi") is not None:
        print("沪深股通成交总额: %s 亿（数据日 %s，≠ 净买入）"
              % (fmt_num(north_net["turnover_yi"]), north.get("date") or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
