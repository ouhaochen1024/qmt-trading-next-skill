"""QMT Bridge 客户端 — 跨平台 HTTP/WebSocket 客户端（无需安装 xtquant）。

通过 Mixin 组合模式将行情、交易、数据下载等功能拆分到独立模块，
最终由 ``QMTClient`` 类统一继承，对外提供完整的 API 访问能力。

架构说明:
    BaseClient 提供底层 HTTP 传输（_get/_post/_delete），所有 Mixin
    通过 self._get() 等方法与服务端通信，无需依赖 xtquant 库。
"""

from qmb_vendor.base import BaseClient
from qmb_vendor.market import MarketMixin
from qmb_vendor.tick import TickMixin
from qmb_vendor.sector import SectorMixin
from qmb_vendor.calendar import CalendarMixin
from qmb_vendor.financial import FinancialMixin
from qmb_vendor.instrument import InstrumentMixin
from qmb_vendor.option import OptionMixin
from qmb_vendor.etf import ETFMixin
from qmb_vendor.cb import CBMixin
from qmb_vendor.futures import FuturesMixin
from qmb_vendor.meta import MetaMixin
from qmb_vendor.download import DownloadMixin
from qmb_vendor.formula import FormulaMixin
from qmb_vendor.hk import HKMixin
from qmb_vendor.tabular import TabularMixin
from qmb_vendor.utility import UtilityMixin
from qmb_vendor.trading import TradingMixin
from qmb_vendor.credit import CreditMixin
from qmb_vendor.fund import FundMixin
from qmb_vendor.smt import SMTMixin
from qmb_vendor.bank import BankMixin
from qmb_vendor.websocket import WebSocketMixin


class QMTClient(
    MarketMixin,
    TickMixin,
    SectorMixin,
    CalendarMixin,
    FinancialMixin,
    InstrumentMixin,
    OptionMixin,
    ETFMixin,
    CBMixin,
    FuturesMixin,
    MetaMixin,
    DownloadMixin,
    FormulaMixin,
    HKMixin,
    TabularMixin,
    UtilityMixin,
    TradingMixin,
    CreditMixin,
    FundMixin,
    SMTMixin,
    BankMixin,
    WebSocketMixin,
    BaseClient,
):
    """QMT Bridge 全功能客户端。

    通过 HTTP 请求与 QMT Bridge 服务端通信，封装了行情查询、数据下载、
    交易委托、两融业务、银证转账等全部功能。

    行情数据类方法无需认证即可使用；交易类方法需要提供 API Key。

    示例::

        from qmt_bridge import QMTClient

        # 仅查询行情（无需 API Key）
        client = QMTClient("192.168.1.100")
        df = client.get_history("000001.SZ", period="1d", count=60)

        # 交易操作（需要 API Key）
        client = QMTClient("192.168.1.100", api_key="your-key")
        result = client.place_order("000001.SZ", order_type=23, order_volume=100)
    """


__all__ = ["QMTClient"]
