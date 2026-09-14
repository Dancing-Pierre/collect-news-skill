# -*- coding: utf-8 -*-
"""默认数据源（tophub 今日热榜·澎湃）→ Claude 择要 10 条 → 100±10字扩写 → 公众号 HTML。

路径已根化：脚本无论放哪都能定位到项目根的 文章模板.txt 与 产出/ 目录。
图片策略：优先沿用澎湃详情页首图（imgpai.thepaper.cn）；源无图则 Bing 按标题取图；再失败回退 DEFAULT_IMG。
"""
import locale
import os
from datetime import datetime

import requests
from lxml import etree

# 项目根：本脚本位于 数据源/今日热榜澎湃/ 下，上溯两级
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_PATH = os.path.join(ROOT, "文章模板.txt")
OUTPUT_DIR = os.path.join(ROOT, "产出")
DEFAULT_IMG = "https://img1.bjd.com.cn/2023/08/20/008c01906b4a4d081b62a119a7a51994a9de2d7a.jpeg"


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


# Claude 择要 10 条：title(≤10字) / content(100±10字扩写) / source_img(澎湃首图，空则Bing按title取)
# 数据源：tophub 今日热榜·澎湃 2026-09-14 采集
ITEMS = [
    {
        "title": "金砖合作启新程",
        "content": "9月12日至13日，习近平赴印度出席金砖会晤。王毅总结此访三目标：为金砖合作增效，提创新发展、和平稳定、文明互鉴、全球治理四大先锋；为全球南方赋能，倡议人工智能开源普惠；为中印领航，与莫迪就做伙伴达成共识。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/1789311926212_TPAYyh_1789311926297.png",
    },
    {
        "title": "敬一丹谢幕",
        "content": "9月13日，敬一丹因病逝世，享年71岁。她从林场播音员成长为央视新闻评论部标志性人物，主持《焦点访谈》20年，三获金话筒奖，以舆论监督与温润表达深入人心。40余年职业生涯刻下“理性、温和、有痛感”印记，退休不退场。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/1789274133024_Epymij_1789274133309.png",
    },
    {
        "title": "上海押注核聚变",
        "content": "全球核聚变路线未定，托卡马克、仿星器、氘-氦3各有软肋。上海多路径并举，孵化星环聚能、东昇聚变等独角兽，储备激光、仿星器、场反多路线项目。上海国投累计投资超10亿元、撬动百亿社会资本，已成全球聚变装置密度最高城市。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/1789256241314_ePedCS_1789256241564.png",
    },
    {
        "title": "AI巨头呼吁减速",
        "content": "Anthropic CEO阿莫代伊撰文呼吁放缓前沿AI，AI毁灭人类概率不止10%。研究员离职爆料两大巨头冲向自我改进的超级智能，公司高管承认十年内AI灭绝人类概率超10%，马斯克与奥特曼罕见赞同，呼吁开放独立评估。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/1789272482938_QB2mec_1789272483202.png",
    },
    {
        "title": "商鞅三十年一票难求",
        "content": "话剧《商鞅》首演三十周年纪念演出在上海上演，所有场次早早售罄。1996年首版主演尹铸胜等悉数到场，传承特别场将现三代“商鞅”同台。该剧曾囊括中国戏剧界所有最高荣誉，换了几代演员仍生命力旺盛，为上话扛鼎之作。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/1789202451352_M586tB_1789273722358.jpg",
    },
    {
        "title": "婚恋纠纷非免死牌",
        "content": "贵州男子杀妻分尸被判无期、襄阳男子杀女友被判死缓，检方均抗诉。法学教授指出，此类婚恋纠纷杀人案适用死刑本应慎重，但手段残忍、分尸抛尸、主观恶性极大者，即使有从宽情节也未必排除死刑。贴“情感纠纷”标签从轻恐冲击司法公正。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/1789286216223_aP4Ydk_1789286216405.png",
    },
    {
        "title": "店主举报遭百次投诉",
        "content": "山东菏泽烧烤店主举报元代沉船文物遗失后，店铺两月内被5部门检查15次。12345热线该店投诉120余件，116件来自同一举报人，其两年反映问题538件涉60余家店铺。山东省文旅厅已指导菏泽组建联合调查组，调查仍在进行。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/1789292048247_FdAMj2_1789292048465.png",
    },
    {
        "title": "假安全培训多地辟谣",
        "content": "兴安盟卫健委声明警惕“安全健康教育网”假借培训发函要求扫码看直播。该机构已被福建龙岩、广东、河北唐山等多地官方辟谣，河北曾披露其假冒政府机关伪造“红头文件”。其域名主办单位中诺普宣教育科技公司实缴资本仅2万元。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/1789308291351_SNGfyj_1789308291597.png",
    },
    {
        "title": "肖思远弟弟选拔提干",
        "content": "卫国戍边烈士肖思远的弟弟肖荣基，经组织严格考核选拔提干，进入陆军步兵学院深造。2020年肖思远在边境冲突中牺牲。2022年18岁的肖荣基追随兄长从军，入伍后2次荣立三等功并入党，2025年参加抗战胜利80周年阅兵。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/20260913/5a7fee72-a054-4ef2-a466-c571fd57e724.jpg",
    },
    {
        "title": "宜居社会需可供性",
        "content": "某手机“魔法画报”难退出引发争议。虽澄清未延误求救，但界面隐藏退出键、缺文字提示，对老人与紧急状态者构成障碍。评论引入“可供性”概念：功能存在不等于能方便使用。宜居社会不应让人都成系统专家，应让环境主动向人伸手。",
        "source_img": "https://imgpai.thepaper.cn/newpai/image/20260913/55e3b078-67c6-4531-84de-ba8beed663f6.jpg",
    },
]


def build_rows():
    """源图优先，缺失走 Bing，再失败回退默认图。返回渲染用 rows。"""
    rows = []
    for it in ITEMS:
        img = it["source_img"]
        if not img:
            img = get_image_url(it["title"]) or DEFAULT_IMG
        rows.append({"detail_new": it["content"], "ai_title": it["title"], "image_url": img})
    print(f"已构建 {len(rows)} 条")
    return rows


def render_html(rows):
    locale.setlocale(locale.LC_CTYPE, "Chinese")
    formatted_date = datetime.now().strftime("——%Y年%m月%d日")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    totle_html = ""
    for idx, row in enumerate(rows, start=1):
        detail = row["detail_new"]
        title = row["ai_title"]
        url = row["image_url"] or DEFAULT_IMG
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
    out_name = os.path.join(OUTPUT_DIR, f"{formatted_date}.html")
    with open(out_name, "w", encoding="utf-8") as f:
        f.write(all_html + "\n")
    return out_name


if __name__ == "__main__":
    # 自检：正文长度应落在 90-110 字
    for idx, it in enumerate(ITEMS, 1):
        n = len(it["content"])
        flag = "OK" if 90 <= n <= 110 else "!!"
        print(f"[{flag}] {idx:02d} {it['title']} -> {n}字")
    rows = build_rows()
    out = render_html(rows)
    print(f"已输出: {out}")
