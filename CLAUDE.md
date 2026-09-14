# 研公资讯汇 · 生产规范（CLAUDE 必读）

本文件是本项目的内容生产硬性规定，每次会话生效，优先级高于默认行为。

## 角色与目标
- 角色：采集 → 由 Claude 汇总 → 输出公众号 HTML（发布到「皮埃尔视界」微信公众平台）。
- 原流程走讯飞星火 AI 汇总标题，现改为 **Claude 直接汇总**，不依赖第三方 AI 标题接口。

## 采集与数据源
- **默认数据源**：tophub 今日热榜·澎湃（`https://tophub.today/n/wWmoO5Rd4E`），列表页 20 条 → 详情页 thepaper.cn 正文。
- 备用数据源：华图时政（`ah.huatu.com/szrd/`），见 `sources/huatu/`。
- 各数据源独立成文件夹，互不干扰；正文/图片直接采用源数据改写，不照搬原文。

## 汇总（核心编辑规则）
1. **择要 10 条**：从采集到的全部条目中，按 **重要程度** 筛选保留 **10 条**（不多不少）。
   - 重要性排序参考：国家级政策/突发外交冲突 > 财政货币大动作 > 行业产业规划 > 民生与监管个案。
2. **正文扩写至 100±10 字**：每条新闻正文在原文基础上适当扩写，控制在 **90-110 字**之间，补充关键主体、数据、因果，保持客观。
3. **精炼标题**：每条配 ≤10 字标题，突出专业性与关键信息。
4. **配图**：优先沿用源详情页首图；源无图则 `get_image_url`（Bing 图搜）按标题取图；再失败回退 `DEFAULT_IMG`。

## 输出
1. **HTML**：套用 `templates/<theme>/template.html` + `card.html`（当前主题 `blue`），**只渲染上述 10 条**卡片，文件名 `——YYYY年MM月DD日.html`。切换主题仅需改生成器顶部 `THEME` 变量并在 `templates/` 下新建同名主题目录（内置 `blue`/`dark`/`green`/`red`/`elegant`，占位符契约见 `templates/README.md`）。
2. **文章摘要**：120 字以内，覆盖当日要点，供公众号「摘要」字段。
3. **文章标题**：1 个吸引人的主标题 + 若干备选，前置最具传播力的关键词，适合信息流点击。

## 文件约定
- 目录结构：`sources/<source>/`（采集脚本+原始数据）、`sources/_renderer.py`（共享渲染层）、`output/`（仅当日 HTML）、`templates/<theme>/`（主题模板，含 `template.html`+`card.html`）与规范文档置于项目根。
- `sources/_renderer.py`：共享层（取图 `get_image_url`、主题渲染 `render_html`、字数自检 `check_items`），两个生成器复用，消除重复。
- `sources/thepaper/generate_tophub.py`：默认数据源生成器（择要10条+100字+Bing/源图），AI 汇总环节由会话人工完成。
- `sources/huatu/generate_today.py`：备用源生成器（同规范）。
- `requirements.txt`：依赖（`requests`+`lxml`），新环境 `pip install -r requirements.txt`。
- 生成器路径已根化（上溯到项目根定位 `templates/<theme>/` 与 `output/`），移动位置不影响运行。

## 红线
- 未经用户主动要求，**不得执行 git commit / 分支等操作**。
- 路径用双引号、正斜杠；危险操作（删除/覆盖）前先确认。
