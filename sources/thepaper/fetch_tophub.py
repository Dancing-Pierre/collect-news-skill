# -*- coding: utf-8 -*-
"""采集 tophub 今日热榜·澎湃：20条列表 → 详情页正文+首图。
从 thepaper.cn 详情页 __NEXT_DATA__ JSON 提取 content(正文HTML) 与 sharePic(首图)。
输出 tophub_list_today.json / tophub_detail_today.json。
"""
import json
import os
import re
import time

import requests
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
LIST_URL = "https://tophub.today/n/wWmoO5Rd4E"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}
PLACEHOLDER = "focusNewsWwwBig.png"  # 频道默认占位图，需排除


def fetch_list():
    r = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    r.encoding = "utf-8"
    tree = etree.HTML(r.text)
    items, seen = [], set()
    for a in tree.xpath('//a[contains(@href,"thepaper.cn")]'):
        title = (a.text or "").strip()
        href = a.get("href", "")
        if title and href and href not in seen:
            seen.add(href)
            items.append({"title": title, "url": href})
    items = items[:20]
    with open(os.path.join(HERE, "tophub_list_today.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"列表采集完成：{len(items)} 条")
    return items


def _pick_img(content_html, share_pic):
    """content 内 imgpai 图优先，其次 sharePic，排除占位图。"""
    tree = etree.HTML(content_html)
    for s in tree.xpath("//img/@src | //img/@data-src"):
        if "imgpai.thepaper.cn" in s and PLACEHOLDER not in s:
            return s.split("?")[0]
    if share_pic and PLACEHOLDER not in share_pic and "imgpai.thepaper.cn" in share_pic:
        return share_pic.split("?")[0]
    return ""


def fetch_detail(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.encoding = "utf-8"
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                      r.text, re.S)
        if not m:
            return {"content": "", "img": ""}
        cd = json.loads(m.group(1))["props"]["pageProps"]["detailData"]["contentDetail"]
        content_html = cd.get("content", "") or ""
        tree = etree.HTML(content_html)
        paras = [p.strip() for p in tree.xpath("//p//text()") if p and p.strip()]
        text = "\n".join(paras)
        img = _pick_img(content_html, cd.get("sharePic", ""))
        return {"content": text, "img": img}
    except Exception as e:
        print(f"详情采集失败 {url}: {e}")
        return {"content": "", "img": ""}


def main():
    items = fetch_list()
    details = []
    for i, it in enumerate(items, 1):
        print(f"[{i:02d}/{len(items)}] {it['title'][:30]}")
        d = fetch_detail(it["url"])
        d["title"] = it["title"]
        d["url"] = it["url"]
        details.append(d)
        time.sleep(0.4)
    with open(os.path.join(HERE, "tophub_detail_today.json"), "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f"详情采集完成：{len(details)} 条 -> tophub_detail_today.json")


if __name__ == "__main__":
    main()
