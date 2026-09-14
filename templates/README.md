# 主题开发指南

每个主题是 `templates/` 下的一个目录，包含两个文件：

| 文件 | 作用 | 占位符 |
|---|---|---|
| `template.html` | 外层包壳（标题 banner + 日期 + 卡片区 + 页脚） | `{cards}`（拼接后的全部卡片）、`{today_time}`（日期，如 `——2026年09月14日`） |
| `card.html` | 单条卡片片段（序号徽章 + 图片 + 正文） | `{idx}`（01–10）、`{title}`、`{detail}`、`{url}`（图片地址） |

渲染时，生成器对每条新闻替换 `card.html` 的四个占位符并拼入 `{cards}`，再替换 `{today_time}`，写出 `output/——YYYY年MM月DD日.html`。**不替换任何样式**——主题完全由这两个 HTML 文件决定，换主题不改内容。

## 内置主题

| 主题 | 目录 | 风格 |
|---|---|---|
| blue | `blue/` | 默认。沿用 96weixin 编辑器 banner + 蓝色卡片（生产在用） |
| dark | `dark/` | 深色商务，金色点缀，适合科技/晚间 |
| green | `green/` | 政务绿，端庄清新 |
| red | `red/` | 喜庆红，适合节庆/重大政策 |
| elegant | `elegant/` | 水墨极简，米白底 + 朱砂点缀，文雅留白 |

> `dark`/`green`/`red`/`elegant` 均为纯内联样式，不依赖外部 CDN 图片，微信公众号编辑器内最稳健。

## 切换主题

改生成器顶部 `THEME` 变量即可（`sources/thepaper/generate_tophub.py` 与 `sources/huatu/generate_today.py` 各有一个）：

```python
THEME = "dark"   # blue / dark / green / red / elegant
```

## 新建主题

1. `templates/<新名>/` 下新建 `template.html` 与 `card.html`。
2. 两个文件分别放入上表对应占位符（缺一不可）。
3. 主题名写入生成器 `THEME`，运行即生效，无需改任何 Python。

### 注意

- 微信公众号会剥离 `<style>` 与部分 class 样式，**一律用内联 `style="..."`**。
- 字体用 `微软雅黑, 'Microsoft YaHei'`；图片用 `<img>` 并给 `width:100%`。
- `{idx}` 在 `card.html` 中可出现多次（徽章与正文序号各一次），渲染时统一替换。
