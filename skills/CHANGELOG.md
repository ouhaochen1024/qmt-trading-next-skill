# Skill 包版本记录

本仓库 **Skills 包**版本见 [`VERSION`](VERSION)（仓库无 pyproject.toml）。发版时改 `VERSION` 并在此登记，再打 Git tag（建议 `v主.次.修订`）。

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.3.0 | 2026-10-29 | 补齐复盘三件套（涨跌家数/板块/北向）：新增盘面速览脚本 `market_summary.py`（涨跌家数/涨停跌停/成交额/板块排行/北向口径）；`_shared` 新增 `get_market_breadth` / `get_northbound` / `get_sector_rank` / `get_sector_boards` / `get_sector_stocks_detail` / `get_tick_details`；market-watch 与 sector-theme 解除 501 降级（板块名改为腾讯行业/概念/地域分类，指数板块名不再适用）；北向净额明确标注"交易所已停止披露" |
| 1.2.0 | 2026-10-27 | 修复 `lastClosed`/`lastClose` 字段错配（涨跌幅、当日盈亏、复盘基线恢复）；移除 `.env` 机制，统一 `config.ini`；real-time WS 脚本改连真实端点；缺 K 下载降级不再中断；10 个 501 技能加显著降级横幅；修正失效示例与死链 |
| 1.1.2 | 2026-09-21 | 产物路径可移植：`reports/` 相对工作区根（monorepo 或 Agent skills 根），禁止依赖机器绝对路径 |
| 1.1.1 | 2026-09-21 | 澄清安装布局：`_shared` 须与各 Skill 同级复制（不注册为 Skill）；修正一键安装/更新提示词 |
| 1.1.0 | 2026-09-21 | 复盘：客观证据包 + 三角色专家规程；阈值 `thresholds.yaml`；`--eval-mode=evidence` |
| 1.0.0 | 2026-09 | 初版 Skill 包（含 setup / 交易 / 复盘等） |

已安装用户请按 [README「更新」](../README.md#更新) 拉取最新版，并核对本地 `skills/VERSION`。
