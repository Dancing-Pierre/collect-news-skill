# -*- coding: utf-8 -*-
"""共享渲染层：图片取图 + 主题 HTML 渲染 + 正文字数自检。

供 sources/thepaper、sources/huatu 两个生成器复用，消除重复代码（DRY）。
单一职责（SRP）：本模块只负责“数据 → HTML 文件”，不关心条目怎么来、怎么扩写。

主题契约（templates/<theme>/ 下两个文件）：
  - template.html  外层包壳，含占位符 {cards}（拼接后的全部卡片）与 {today_time}（日期）
  - card.html      单条卡片片段，含占位符 {idx} {title} {detail} {url}
渲染即逐条替换 card.html 占位符并拼入 {cards}，再替换 {today_time}，写出 HTML。

新增主题：在 templates/ 下新建目录，放上述两个文件即可，无需改本模块。
"""
import locale
import os
from datetime import datetime

import requests
from lxml import etree

# sources/_renderer.py 上溯一级即项目根
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(ROOT, "templates")
OUTPUT_DIR = os.path.join(ROOT, "output")
DEFAULT_IMG = "https://img1.bjd.com.cn/2023/08/20/008c01906b4a4d081b62a119a7a51994a9de2d7a.jpeg"


def get_image_url(search_name):
    """Bing 图搜按标题取一张图，失败返回空串。"""
    if not search_name or not search_name.strip():
        return ""
    url = "https://cn.bing.com/images/async"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 "
                      "Mobile Safari/537.36 Edg/134.0.0.0"
    }
    params = {
        "q": search_name, "first": 0, "count": 1, "cw": 437, "ch": 603,
        "relp": 1, "datsrc": "I", "layout": "ColumnBased_Landscape",
        "apc": 0, "mmasync": 2, "iid": "images.5306",
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.encoding = "utf-8"
        tree = etree.HTML(r.text)
        for attr in ("data-src", "src", "data-murl"):
            lst = tree.xpath(f"//img/@{attr}")
            if lst:
                iu = lst[0]
                if "?" in iu:
                    iu = iu.split("?")[0]
                return iu
        return ""
    except Exception as e:
        print(f"获取图片链接失败: {e}")
        return ""


def check_items(items, lo=90, hi=110):
    """自检每条 content 字数是否落在 [lo, hi]，打印 [OK]/[!!]，返回是否全通过。"""
    ok = True
    for idx, it in enumerate(items, 1):
        n = len(it["content"])
        flag = "OK" if lo <= n <= hi else "!!"
        if flag == "!!":
            ok = False
        print(f"[{flag}] {idx:02d} {it['title']} -> {n}字")
    return ok


def _read_theme(theme, name):
    path = os.path.join(TEMPLATES_DIR, theme, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def render_html(theme, rows, default_img=DEFAULT_IMG):
    """rows: [{detail_new, ai_title, image_url}, ...] → 渲染并写出 output/——日期.html，返回路径。"""
    # 中文 locale 仅 Windows 可用；失败则回退，strftime 仍可正常输出中文日期
    try:
        locale.setlocale(locale.LC_CTYPE, "Chinese")
    except Exception:
        pass

    date = datetime.now().strftime("——%Y年%m月%d日")
    wrapper = _read_theme(theme, "template.html")
    card_tpl = _read_theme(theme, "card.html")

    cards = ""
    for idx, row in enumerate(rows, 1):
        i = f"{idx:02d}" if idx < 10 else str(idx)
        url = row.get("image_url") or default_img
        cards += (card_tpl
                  .replace("{idx}", i)
                  .replace("{title}", row.get("ai_title", ""))
                  .replace("{detail}", row.get("detail_new", ""))
                  .replace("{url}", url))

    html = wrapper.replace("{cards}", cards).replace("{today_time}", date)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, f"{date}.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html + "\n")
    return out
