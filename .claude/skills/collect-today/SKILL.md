---
name: collect-today
description: "研公资讯汇当日采集与输出：跑 fetch_tophub.py 采集今日热榜·澎湃 20 条 → Claude 择要 10 条 + 100±10字扩写 + ≤10字标题 → 更新 generate_tophub.py 的 ITEMS → 生成公众号 HTML → 给出摘要与标题。每日采集输出流程由此技能驱动。"
---

# 当日采集与输出

本技能驱动「研公资讯汇」公众号的每日采集→汇总→产出流程。规则以项目根 `CLAUDE.md` 为准，本文件只固化操作步骤。

适用场景：用户说"完成今天的采集""今日采集输出""跑一下采集"等当日生产请求。

---

## Step 0：环境准备（仅首次 / 缺依赖时）

采集与生成依赖 `requests` + `lxml`。若运行报 `ModuleNotFoundError`，先装依赖（项目根有 `requirements.txt`）：

```bash
pip install -r requirements.txt
```

> Windows 终端中文可能因 GBK 显示乱码，属正常；采集/生成命令统一加 `PYTHONIOENCODING=utf-8`。

## Step 1：采集今日原始数据

跑采集脚本（tophub 列表 20 条 → 澎湃详情页正文 + 首图）：

```bash
cd sources/thepaper && PYTHONIOENCODING=utf-8 python fetch_tophub.py
```

- 产出 `sources/thepaper/tophub_list_today.json`、`sources/thepaper/tophub_detail_today.json`。
- 控制台中文可能因 Windows GBK 终端显示乱码，属正常，JSON 本身为 UTF-8。
- 若采集失败（网络/源站结构变更），改用备用源 `sources/huatu/generate_today.py`，并向用户报告。

## Step 2：读取并理解原始数据

用 Read 工具读 `sources/thepaper/tophub_detail_today.json`，逐条理解 20 条的 title/content/img/url。

- content 为空（详情页未采到正文）的条目：优先用 WebSearch 按标题补素材；WebFetch 对 thepaper.cn 域名常被网络策略拦截，直接走 WebSearch。
- 同一事件常有多条重复角度，按主题去重。

## Step 3：择要 10 条（Claude 直接汇总）

从 20 条中按 **重要程度** 筛选 **不多不少 10 条**。重要性排序参考：

1. 国家级政策 / 突发外交冲突
2. 财政货币大动作
3. 行业产业规划
4. 民生与监管个案

编辑去重原则：与昨日已发布条目（查 `output/` 下前一日的 HTML）**主题完全重复**的，优先剔除；当日热榜霸榜的同一主题（如占 5 条）保留 1 条最具信息量的即可，避免连日堆叠。

## Step 4：扩写正文 + 精炼标题 + 配图

逐条：

- **标题**：≤10 字，突出专业性与关键信息。
- **正文**：在原文基础上扩写到 **90–110 字**（硬性区间，脚本会自检）。补充关键主体、数据、因果，保持客观。逐条**精确数字符数**（含标点；数字、英文字母每字符计 1），超区间则裁剪/增补。
- **配图**：优先沿用澎湃详情页首图（`img` 字段，`imgpai.thepaper.cn`）；源无图则置空字符串，由 `generate_tophub.py` 的 `resolve_images()` 走 Bing 取图再回退 `DEFAULT_IMG`。

## Step 5：更新生成器 ITEMS

用 Edit 工具替换 `sources/thepaper/generate_tophub.py` 中的 `ITEMS` 列表：

- 同步更新注释行 `# 数据源：tophub 今日热榜·澎湃 YYYY-MM-DD 采集` 的日期。
- 每条结构固定：`title` / `content` / `source_img`。
- 正文中若需引号，用中文弯引号 `“”`，**不要**用 ASCII `"`，避免与 Python 字符串定界符冲突。

## Step 6：运行生成器

```bash
cd sources/thepaper && PYTHONIOENCODING=utf-8 python generate_tophub.py
```

- 脚本先自检每条正文字数，`[OK]` 表示落在 90–110；出现 `[!!]` 必须回到 Step 4 修正后重跑。
- 产出 `output/——YYYY年MM月DD日.html`（仅 HTML，不再生成 CSV）。
- 主题切换：改 `generate_tophub.py` 顶部 `THEME = "blue"` 为 `templates/` 下任一主题目录名即可（内置 `blue`/`dark`/`green`/`red`/`elegant`，开发指南见 `templates/README.md`），切换 HTML 风格不改内容。

## Step 7：校验产出

```bash
ls -la output/  # 确认当日 HTML 已生成、日期正确
```

确认：HTML 文件名日期为当天；图片非空（源图优先，无回退默认图）。

## Step 8：给出摘要与标题

向用户交付：

- **文章标题**：1 个主标题 + 2–3 个备选，前置最具传播力的关键词，适合信息流点击。格式建议 `研公资讯汇丨M.D：关键词1、关键词2、关键词3`。
- **文章摘要**：≤120 字，覆盖当日 10 条要点，供公众号「摘要」字段。

## 注意

- 路径一律双引号、正斜杠。
- 未经用户主动要求，**不得** git commit / 分支操作。
- 危险操作（删除/覆盖）前先确认。
- 数据源独立成文件夹，互不干扰；正文/图片采用源数据改写，不照搬原文。
