# -*- coding: utf-8 -*-
"""备用数据源（华图时政 ah.huatu.com/szrd/）→ Claude 撰写精炼标题 → 公众号 HTML。

渲染/取图统一走 sources/_renderer.py（共享层，消除重复）。AI 汇总环节由会话人工完成。
"""
import json
import os
import sys

# 把 sources/ 加入搜索路径以导入共享渲染层
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _renderer import get_image_url, render_html, DEFAULT_IMG

HERE = os.path.dirname(os.path.abspath(__file__))
# 主题：切换只需改此变量 + 在 templates/ 下新建 <主题>/ 目录（含 template.html 与 card.html）
THEME = "blue"
RAW_PATH = os.path.join(HERE, "raw_news.json")

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


def build_data():
    """读取采集原文，剔除板块标题行并去掉前缀序号，按顺序绑定 Claude 标题与图片。返回 rows。"""
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        lines = json.load(f)
    # 仅保留实际新闻条目（以“数字、”开头），跳过“一、全球”这类板块标题
    items = [ln for ln in lines if ln and ln[0].isdigit()]
    if len(items) != len(TITLES):
        raise SystemExit(f"条目数({len(items)})与标题数({len(TITLES)})不一致，请核对")
    rows = []
    for detail, title in zip(items, TITLES):
        body = "、".join(str(detail).split("、")[1:])  # 去掉“数字、”前缀
        img = get_image_url(title) or DEFAULT_IMG
        rows.append({"detail_new": body, "ai_title": title, "image_url": img})
    print(f"已构建 {len(rows)} 条")
    return rows


if __name__ == "__main__":
    rows = build_data()
    out = render_html(THEME, rows)
    print(f"已输出: {out}")
