# collect-news-skill

A Claude Code skill that turns daily news crawling into ready-to-publish WeChat public-account HTML. Crawl → Claude selects & expands → themed HTML output.

See it live on the WeChat official account **皮埃尔视界** (Pierre's View).

> 中文文档见 [README.zh-CN.md](README.zh-CN.md)。

## How it works

1. **Crawl** — `fetch_tophub.py` pulls the top-20 items from the tophub 澎湃 hot-list, then fetches the full article body + lead image from each thepaper.cn detail page.
2. **Curate** — Claude picks the **10 most important** stories, expands each body to **90–110 characters**, and writes a **≤10-character** headline.
3. **Render** — `generate_tophub.py` fills the chosen theme template and writes one HTML file: `output/——YYYY年MM月DD日.html`.

The whole flow is driven by the `collect-today` skill — just say "collect today" and Claude runs end-to-end.

## Directory layout

```
collect-news-skill/
├─ sources/
│  ├─ thepaper/                # default source (tophub hot-list → thepaper.cn detail)
│  │  ├─ fetch_tophub.py       # crawler: 20 list items + thepaper detail body/image
│  │  ├─ generate_tophub.py    # generator: 10-item pick + 100±10 chars + source/Bing image
│  │  ├─ tophub_list_today.json     # raw list (crawled, gitignored)
│  │  └─ tophub_detail_today.json   # raw detail (crawled, gitignored)
│  └─ huatu/                   # backup source (ah.huatu.com/szrd/)
│     ├─ generate_today.py     # generator (same spec, Claude-curated)
│     └─ raw_news.json
├─ templates/
│  └─ blue/template.html       # themed HTML template (switch via the THEME var)
├─ output/                     # generated daily HTML (gitignored)
├─ .claude/skills/collect-today/SKILL.md   # the callable skill
└─ CLAUDE.md                   # production rules (auto-loaded each session)
```

## Usage

**Default source (recommended):**
```bash
python sources/thepaper/generate_tophub.py
```
The `ITEMS` list inside the generator holds Claude's 10 curated stories (≤10-char title, 100±10-char body). Running it outputs `output/——<today>.html`.

> Crawling (tophub list + thepaper detail) must run first to land `tophub_detail_today.json`, after which Claude curates the picks in-session and fills `ITEMS`. The skill automates this entire loop.

## Switching themes

Create a new directory under `templates/` (e.g. `templates/dark/template.html`), then set `THEME = "dark"` at the top of the generator. No content changes — only the HTML styling swaps.

## Rules

See `CLAUDE.md` (auto-loaded each session): pick 10 items, 100±10-char bodies, source-image-first with Bing fallback, ≤120-char summary + click-worthy headline.
