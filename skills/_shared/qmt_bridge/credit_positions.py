"""qmt_bridge.credit_positions 兼容 shim → vendor 的信用持仓拆分模块。

注意：包级 __getattr__ 对 `from qmt_bridge.sub import X` 形式不生效，
所以子模块必须以真实文件形式存在。
"""

from qmb_vendor.credit_positions import *  # noqa: F401,F403
from qmb_vendor.credit_positions import (  # noqa: F401  显式列出常用名
    COMPACT_TYPE_FIN_BUY,
)
