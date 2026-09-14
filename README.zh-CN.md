# collect-news-skill

一个 Claude Code 技能：把每日新闻采集变成可直接发布的微信公众号 HTML。采集 → Claude 择要扩写 → 主题化 HTML 输出。

效果可见微信公众号 **皮埃尔视界**。

> English: [README.md](README.md).

## 工作原理

1. **采集** — `fetch_tophub.py` 抓取 tophub 今日热榜·澎湃的 20 条，再逐条抓取 thepaper.cn 详情页正文与首图。
2. **汇总** — Claude 择出 **10 条最重要的**新闻，每条正文扩写到 **90–110 字**，并配 **≤10 字**标题。
3. **渲染** — `generate_tophub.py` 套用选定主题模板，输出一份 HTML：`output/——YYYY年MM月DD日.html`。

整套流程由 `collect-today` 技能驱动——只需说"采集今天"，Claude 端到端跑完。

## 目录结构

```
collect-news-skill/
├─ sources/
│  ├─ _renderer.py            # 共享渲染层（取图 + 主题渲染 + 字数自检，供两个源复用）
│  ├─ thepaper/                # 默认数据源（tophub 热榜 → 澎湃详情）
│  │  ├─ fetch_tophub.py       # 采集：20 条列表 + 澎湃详情正文/首图
│  │  ├─ generate_tophub.py    # 生成器：择要10条 + 100±10字 + 源图/Bing
│  │  ├─ tophub_list_today.json     # 当日列表原始数据（采集落盘，已忽略入库）
│  │  └─ tophub_detail_today.json   # 当日详情原始数据（采集落盘，已忽略入库）
│  └─ huatu/                   # 备用数据源（ah.huatu.com/szrd/）
│     ├─ generate_today.py     # 生成器（同规范，Claude 汇总）
│     └─ raw_news.json
├─ templates/
│  ├─ README.md                # 主题开发指南（占位符契约）
│  ├─ blue/  (template.html + card.html)   # 默认主题
│  ├─ dark/  ...                            # 深色商务
│  ├─ green/ ...                            # 政务绿
│  ├─ red/   ...                            # 喜庆红
│  └─ elegant/ ...                          # 水墨极简
├─ output/                     # 生成的当日 HTML（已忽略入库）
├─ requirements.txt            # 依赖（requests + lxml）
├─ .claude/skills/collect-today/SKILL.md   # 可调用技能
└─ CLAUDE.md                   # 生产规范（每次会话自动加载）
```

## 环境准备

```bash
pip install -r requirements.txt
```

依赖：`requests`（HTTP 采集）、`lxml`（HTML 解析）。Windows 终端运行采集/生成命令时建议加 `PYTHONIOENCODING=utf-8` 避免中文乱码。

## 使用方式

**默认源（推荐）**：
```bash
python sources/thepaper/generate_tophub.py
```
脚本内 `ITEMS` 为 Claude 当期择要的 10 条（标题≤10字、正文100±10字），运行后输出 `output/——当日.html`。

> 采集环节（tophub 列表+澎湃详情）需先跑采集落盘 `tophub_detail_today.json`，再由 Claude 在会话内完成择要与扩写并填入 `ITEMS`。技能把这一整圈自动化了。

## 切换主题

内置 5 套主题：`blue`（默认）、`dark`、`green`、`red`、`elegant`，改生成器顶部 `THEME` 变量即可切换，内容不变只换 HTML 风格：

```python
THEME = "dark"   # blue / dark / green / red / elegant
```

每个主题是 `templates/<名>/` 下的 `template.html`（外壳）+ `card.html`（卡片），占位符契约与新增主题方法见 [`templates/README.md`](templates/README.md)。`blue` 沿用 96weixin banner（生产在用），其余四套为纯内联样式，不依赖外部 CDN，微信公众号编辑器内最稳健。

## 规范
详见 `CLAUDE.md`（每次会话自动加载）：择要10条、正文100±10字、源图优先Bing回退、120字摘要+吸引人标题。
