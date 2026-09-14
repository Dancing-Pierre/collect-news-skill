# -*- coding: utf-8 -*-
"""由 Claude 直接汇总采集数据并生成公众号 HTML。

流程：raw_news.json（采集原文）→ Claude 撰写精炼标题 → Bing 取图 → 套用 文章模板.txt 输出 HTML。
AI 汇总环节由本会话人工完成。
"""
import json
import locale
import os
from datetime import datetime

import requests
from lxml import etree
from os.path import exists

# 项目根：本脚本位于 sources/huatu/ 下，上溯两级
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
# 主题：切换只需改此变量 + 在 templates/ 下新建 <主题>/template.html
THEME = "blue"
OUTPUT_DIR = os.path.join(ROOT, "output")
RAW_PATH = os.path.join(HERE, "raw_news.json")
TEMPLATE_PATH = os.path.join(ROOT, "templates", THEME, "template.html")
DEFAULT_IMG = "https://img1.bjd.com.cn/2023/08/20/008c01906b4a4d081b62a119a7a51994a9de2d7a.jpeg"

# Claude 汇总的精炼标题（≤10字，突出专业性与关键信息），与 raw_news.json 顺序一一对应
TITLES = [
    # 一、全球
    "伊朗驳斥美侵略说",
    "卡塔尔呼吁安全自主",
    "美伊互袭震动欧能源",
    "特朗普欲改名新墨州",
    "泰总理倡泰中一家亲",
    "日借渔港扩海洋监视",
    "美数据中心用地激增",
    # 二、国内
    "中方回应中美AI对话",
    "工信部推通信全球覆盖",
    "工信部育千亿产业集群",
    "文旅部推非遗焕新",
    "台风救灾拨付2.4亿",
    # 三、市场
    "3000亿特别国债注资",
    "央行连22月增持黄金",
    "8月PMI回升至49.8",
    # 四、社会
    "最高法出台AI纠纷意见",
    "央视曝光监测造假案",
]


def get_image_url(search_name):
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


def build_data():
    """读取采集原文，剔除板块标题行，按顺序绑定 Claude 标题与图片。返回 rows。"""
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        lines = json.load(f)
    # 仅保留实际新闻条目（以“数字、”开头），跳过“一、全球”这类板块标题
    items = [ln for ln in lines if ln and ln[0].isdigit()]
    if len(items) != len(TITLES):
        raise SystemExit(f"条目数({len(items)})与标题数({len(TITLES)})不一致，请核对")
    rows = []
    for detail, title in zip(items, TITLES):
        img = get_image_url(title) or DEFAULT_IMG
        rows.append({"detail_new": detail, "ai_title": title, "image_url": img})
    print(f"已构建 {len(rows)} 条")
    return rows


def render_html(rows):
    locale.setlocale(locale.LC_CTYPE, "Chinese")
    formatted_date = datetime.now().strftime("——%Y年%m月%d日")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    totle_html = ""
    for idx, row in enumerate(rows, start=1):
        detail = "、".join(str(row["detail_new"]).split("、")[1:])
        title = row["ai_title"]
        url = row["image_url"]
        if not url:
            url = DEFAULT_IMG
        i = f"{idx:02d}" if idx < 10 else str(idx)
        html = f"""<section class="_editor" draggable="true">
                                    <p>
                                        <br/>
                                    </p>
                                    <section class="_editor" draggable="true">
                                        <section style="display: inline-block; margin-top: 10px;">
                                            <section style="display:flex;justify-content:center;align-items:flex-end;">
                                                <section style="background-color: #b5d5eb;">
                                                    <section style="margin:-3px 3px 3px -3px;">
                                                        <section style="margin-right:4px;font-size:16px;color:#fff;background-color:#23569e;letter-spacing:2px;text-align:center;padding:4px 20px;transform:rotateZ(0deg);">
                                                            <p>
                                                                <span style="font-family: 微软雅黑, &quot;Microsoft YaHei&quot;;"><strong>{i} <span style="font-size: 17.01px;">{title}</span></strong></span>
                                                            </p>
                                                        </section>
                                                    </section>
                                                    <section style="width:16px;height:16px;background-color:#f2c96f;margin-left:auto;margin-top: -12px;">
                                                        <br/>
                                                    </section>
                                                </section>
                                            </section>
                                        </section>
                                    </section>
                                    <section class="_editor" style="width: 95%; margin-right: auto; margin-left: auto;" draggable="true">
                                        <section style="background-color: #cceafa; margin-top: 20px; margin-bottom: 20px; padding-top: 20px; padding-right: 10px; padding-left: 10px;">
                                            <section class="_editor">
                                                <section>
                                                    <img src="{url}"/>
                                                </section>
                                            </section>
                                            <section class="_editor">
                                                <section style="margin-top: 10px; margin-bottom: 10px; color: #000000; font-size: 14px; letter-spacing: 2px; line-height: 1.75em;">
                                                    <p style="text-align: left;">
                                                        <span style="color: rgb(68, 68, 68); text-indent: 28px; font-family: 微软雅黑, &quot;Microsoft YaHei&quot;; font-size: 14px;">{i}、{detail}</span>
                                                    </p>
                                                </section>
                                            </section>
                                        </section>
                                    </section>
                                </section>"""
        totle_html += html

    all_html = content.replace("{datail}", totle_html).replace("{today_time}", formatted_date)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_name = os.path.join(OUTPUT_DIR, f"{formatted_date}.html")
    with open(out_name, "w", encoding="utf-8") as f:
        f.write(all_html + "\n")
    return out_name


if __name__ == "__main__":
    rows = build_data()
    out = render_html(rows)
    print(f"已输出: {out}")
