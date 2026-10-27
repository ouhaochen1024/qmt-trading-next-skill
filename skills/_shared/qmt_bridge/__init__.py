"""qmt_bridge 兼容 shim（仅存在于 skills/_shared 下）。

Skill 脚本历史上 `from qmt_bridge import QMTClient`；本 shim 把它指向
随仓库 vendor 的纯 HTTP 客户端包 `qmb_vendor`（位于 _shared/，无
xtquant 依赖）。真正的信箱/交易执行在 qmt-bridge-next 服务端。
"""

from qmb_vendor import QMTClient  # noqa: F401

__all__ = ["QMTClient"]


def __getattr__(name):  # 惰性子模块（credit_positions 等）
    import importlib

    return importlib.import_module(f"qmb_vendor.{name}")
