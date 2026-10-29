"""SectorMixin — 板块数据客户端方法。

封装了板块（行业/概念/自定义）相关的查询和管理接口，包括：
- 板块列表查询、板块成分股查询
- 自定义板块的创建、删除和成分股管理

底层对应 xtquant 的 ``xtdata.get_sector_list()``、
``xtdata.get_stock_list_in_sector()``、``xtdata.create_sector()`` 等函数。

板块分类说明:
    xtquant 内置了多种板块分类，如"沪深A股"、"上证A股"、"深证A股"、
    "创业板"、"科创板"、行业板块、概念板块等。用户也可以创建自定义板块
    来管理自己的股票池。
"""


class SectorMixin:
    """板块数据客户端方法集合，对应 /api/sector/* 端点。"""

    def get_sector_list(self, board_type: str = "hy") -> list[str]:
        """获取可用的板块名称列表。

        桥接端（qmt-bridge-next）板块来自腾讯：``hy`` 行业 31 个、
        ``gn`` 概念 800+、``dy`` 地域 31 个；``all`` 合并全部。
        名称即「煤炭」「证金持股」「青海」这类板块名，**不含** xtdata 的
        「沪深A股 / 上证50 / 中证500」等指数板块。

        Args:
            board_type: hy 行业 / gn 概念 / dy 地域 / all 全部

        Returns:
            板块名称列表，按涨跌幅降序
        """
        resp = self._get("/api/sector/list", {"type": board_type})
        return resp.get("sectors", [])

    def get_sector_boards(self, board_type: str = "hy") -> list[dict]:
        """获取板块列表明细（含涨跌幅、主力净流入、板块内涨跌家数）。

        Args:
            board_type: hy / gn / dy

        Returns:
            板块字典列表；单条含 ``code`` / ``name`` / ``pct_chg`` /
            ``main_net_inflow_wan``（万元）/ ``up_count`` / ``down_count`` /
            ``member_count`` / ``leader``（领涨股）/ ``pct_chg_5d`` 等
        """
        resp = self._get("/api/sector/list", {"type": board_type})
        return resp.get("boards", [])

    def get_sector_rank(
        self,
        board_type: str = "hy",
        sort: str = "pct_chg",
        order: str = "desc",
        limit: int = 20,
        min_member: int = 0,
    ) -> dict:
        """板块排行（行业 / 概念 / 地域强弱）。

        Args:
            board_type: hy / gn / dy
            sort: 排序字段 — ``pct_chg``（涨跌幅）/ ``main_net_inflow_wan``
                （主力净流入）/ ``turnover_wan`` / ``turnover_rate`` /
                ``pct_chg_5d`` / ``pct_chg_20d`` / ``pct_chg_60d`` /
                ``pct_chg_ytd`` 等
            order: desc 降序 / asc 升序
            limit: 返回条数（1~200）
            min_member: 成分股数量下限，用于过滤迷你概念板块

        Returns:
            ``{type, sort, order, count, items: [...]}``
        """
        resp = self._get("/api/sector/rank", {
            "type": board_type,
            "sort": sort,
            "order": order,
            "limit": limit,
            "min_member": min_member,
        })
        return resp.get("data", {})

    def get_sector_info(self, sector: str = "") -> dict:
        """获取板块元数据信息。

        底层调用 ``xtdata.get_sector_info()``，返回板块的层级结构、
        父节点等元信息。

        Args:
            sector: 板块名称，为空时返回所有板块的信息

        Returns:
            板块元数据字典
        """
        resp = self._get("/api/sector/info", {"sector": sector})
        return resp.get("data", {})

    def get_sector_stocks(self, sector: str) -> list[str]:
        """获取板块成分股代码列表。

        桥接端（qmt-bridge-next）由腾讯板块成分接口提供，返回当前成分。
        ``sector`` 可传板块名（如 ``"煤炭"``）或板块代码（``"pt01801950"``），
        名称以 :meth:`get_sector_list` 返回为准。

        Args:
            sector: 板块名称或代码

        Returns:
            成分股代码列表，如 ``["600997.SH", "601101.SH", ...]``
        """
        resp = self._get("/api/sector_stocks", {"sector": sector})
        return resp.get("stocks", [])

    def get_sector_stocks_detail(
        self,
        sector: str,
        sort: str = "pct_chg",
        order: str = "desc",
        limit: int = 0,
    ) -> dict:
        """获取板块成分股**含行情**的明细（本地排序）。

        Args:
            sector: 板块名称或代码
            sort: 排序字段（``pct_chg`` / ``turnover_wan`` / ``turnover_rate`` 等）
            order: desc / asc
            limit: 0 表示全部

        Returns:
            ``{sector, code, member_count, count, stocks: [代码],
            items: [{code, name, price, pct_chg, ...}]}``
        """
        resp = self._get("/api/sector/stocks", {
            "sector": sector,
            "sort": sort,
            "order": order,
            "limit": limit,
        })
        return resp

    def get_sector_stocks_v2(
        self, sector: str, real_timetag: int = -1
    ) -> list[str]:
        """获取板块成分股列表（支持历史成分查询）。

        底层调用 ``xtdata.get_stock_list_in_sector(sector_name, real_timetag)``，
        当指定 ``real_timetag`` 参数时，可查询板块在某一历史时间点的成分股构成，
        用于回测时获取当时的真实成分。

        Args:
            sector: 板块名称
            real_timetag: 历史时间戳（毫秒），-1 表示使用最新成分

        Returns:
            成分股代码列表
        """
        resp = self._get("/api/sector/stocks", {
            "sector": sector,
            "real_timetag": real_timetag,
        })
        return resp.get("stocks", [])

    # ------------------------------------------------------------------
    # 写操作（自定义板块管理）
    # ------------------------------------------------------------------

    def create_sector_folder(self, folder_name: str) -> dict:
        """创建板块文件夹。

        底层调用 ``xtdata.create_sector_folder()``，在板块树中创建一个
        新的文件夹节点，用于组织自定义板块。

        Args:
            folder_name: 文件夹名称

        Returns:
            操作结果
        """
        return self._post("/api/sector/create_folder", {"folder_name": folder_name})

    def create_sector(self, sector_name: str, parent_node: str = "") -> dict:
        """创建自定义板块。

        底层调用 ``xtdata.create_sector()``，在指定父节点下创建一个
        新的自定义板块。

        Args:
            sector_name: 板块名称
            parent_node: 父节点名称，为空时创建在根目录下

        Returns:
            操作结果
        """
        return self._post("/api/sector/create", {
            "sector_name": sector_name,
            "parent_node": parent_node,
        })

    def add_sector_stocks(self, sector_name: str, stocks: list[str]) -> dict:
        """向板块添加成分股。

        底层调用 ``xtdata.add_sector()``，将指定股票添加到自定义板块中。

        Args:
            sector_name: 板块名称
            stocks: 要添加的股票代码列表

        Returns:
            操作结果
        """
        return self._post("/api/sector/add_stocks", {
            "sector_name": sector_name,
            "stocks": stocks,
        })

    def remove_sector_stocks(self, sector_name: str, stocks: list[str]) -> dict:
        """从板块移除成分股。

        底层调用 ``xtdata.remove_stock_from_sector()``，从自定义板块中
        移除指定股票。

        Args:
            sector_name: 板块名称
            stocks: 要移除的股票代码列表

        Returns:
            操作结果
        """
        return self._post("/api/sector/remove_stocks", {
            "sector_name": sector_name,
            "stocks": stocks,
        })

    def remove_sector(self, sector_name: str) -> dict:
        """删除整个板块。

        底层调用 ``xtdata.remove_sector()``，删除一个自定义板块及其全部成分股。
        注意：内置系统板块不可删除。

        Args:
            sector_name: 要删除的板块名称

        Returns:
            操作结果
        """
        return self._delete("/api/sector/remove", {"sector_name": sector_name})

    def reset_sector(self, sector_name: str, stocks: list[str]) -> dict:
        """重置板块成分股（替换全部）。

        底层调用 ``xtdata.reset_sector()``，用新的股票列表完全替换板块
        中的现有成分股。

        Args:
            sector_name: 板块名称
            stocks: 新的成分股代码列表

        Returns:
            操作结果
        """
        return self._post("/api/sector/reset", {
            "sector_name": sector_name,
            "stocks": stocks,
        })
