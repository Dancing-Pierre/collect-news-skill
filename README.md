# news_crawler_generates_wechat_public_account_articles
新闻爬虫生成微信公众号文章

采集新闻详情，由 Claude 择要 10 条并扩写汇总，再填充成 HTML，方便导入公众号发布。效果可见微信公众号：皮埃尔视界。

## 目录结构

```
wechat_spider_article/
├─ 文章模板.txt            # 公众号 HTML 套版模板（共享）
├─ 数据源/
│  ├─ 今日热榜澎湃/        # 默认数据源（tophub 热榜 → 澎湃详情）
│  │  ├─ fetch_tophub.py      # 采集：tophub 列表 20 条 + 澎湃详情正文/首图
│  │  ├─ generate_tophub.py  # 生成器：择要10条 + 100±10字 + 源图/Bing
│  │  ├─ tophub_list_today.json    # 当日列表原始数据（采集落盘）
│  │  └─ tophub_detail_today.json  # 当日详情原始数据（采集落盘）
│  └─ 华图时政/            # 备用数据源（ah.huatu.com 时政热点）
│     ├─ generate_today.py   # 生成器（同规范，Claude 汇总）
│     └─ raw_news.json
└─ 产出/
   └─ ——YYYY年MM月DD日.html   # 最终公众号 HTML
```

## 使用方式

**默认源（推荐）**：
```bash
python "数据源/今日热榜澎湃/generate_tophub.py"
```
脚本内 `ITEMS` 为 Claude 当期择要的 10 条（标题≤10字、正文100±10字），运行后输出 `产出/——当日.html`。

> 采集环节（tophub 列表+澎湃详情）需先跑采集落盘 `tophub_detail.json`，再由 Claude 在会话内完成择要与扩写并填入 `ITEMS`。

## 规范
详见 `CLAUDE.md`（每次会话自动加载）：择要10条、正文100±10字、源图优先Bing回退、120字摘要+吸引人标题。
