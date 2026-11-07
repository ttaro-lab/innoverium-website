"""홈·사업 페이지·블로그가 함께 쓰는 머리글(GNB), 바닥글(사이트맵), <head> 조각.

메뉴를 바꾸려면 MENU만 고치면 됩니다. build_site.py와 build_blog.py가 모두 이 파일을 씁니다.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
site = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
BASE = site["url"].rstrip("/")


def e(s):
    return html.escape(str(s or ""), quote=True)


# (키, 이름, 주소, 하위메뉴[(이름, 설명, 주소)])
MENU = [
    ("about", "회사소개", "/#about", []),
    ("policy", "정책 기획", "/business/policy/", []),
    ("rnd", "R&D 기획", "/business/rnd/", []),
    ("analysis", "조사분석", "/business/analysis/", []),
    ("research", "연구개발", "/research/", [("스마트팜", "AI 수요 예측 · 그린바이오팜", "/research/#smart-farm")]),
    ("projects", "수행실적", "/#projects", []),
    ("blog", "블로그", "/blog/", []),
]

# 사이트 전체 페이지 목록 (sitemap.xml, llms.txt에 씁니다)
PAGES = [
    ("/", "홈", "정책 기획, R&D 기획, 조사분석, 연구개발 소개와 수행실적"),
    ("/business/policy/", "정책 기획", "지역 산업육성 전략, 기관 R&D 전략계획, 성과관리 체계 설계"),
    ("/business/rnd/", "R&D 기획", "신규 R&D 사업 사전기획·본기획, 기획요소 도출, 연구 인프라 구축 기획"),
    ("/business/analysis/", "조사분석", "기술·특허 동향, 사전타당성, 입지분석·수요조사, 효과성·성과분석"),
    ("/research/", "연구개발 · 스마트팜", "기술이전 특허 기반 AI 수요 예측 엔진과 다품종 정밀환경 그린바이오팜"),
]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">\n'
    '<link rel="stylesheet" href="/assets/site.css">'
)


def header(current=""):
    items = []
    for key, name, href, subs in MENU:
        cur = ' aria-current="page"' if key == current else ""
        if subs:
            sub = "".join(f'<a href="{h}">{e(n)}<small>{e(d)}</small></a>' for n, d, h in subs)
            items.append(f'<li class="has-sub"><a href="{href}"{cur}>{e(name)}</a><div class="sub">{sub}</div></li>')
        else:
            items.append(f'<li><a href="{href}"{cur}>{e(name)}</a></li>')
    items.append('<li class="ask"><a href="/#contact">문의하기</a></li>')
    return (
        '<a class="skip" href="#main">본문 바로가기</a>\n'
        '<header class="hd"><div class="hd-in">'
        f'<a class="logo" href="/"><b>{e(site["name_en"])}</b><span>{e(site["name"])}</span></a>'
        '<button class="menu-btn" aria-label="메뉴 열기" aria-expanded="false" '
        "onclick=\"var g=document.getElementById('gnb');g.classList.toggle('open');this.setAttribute('aria-expanded',g.classList.contains('open'))\">"
        '<i></i><i></i><i></i></button>'
        f'<ul class="gnb" id="gnb">{"".join(items)}</ul>'
        '</div></header>'
    )


def footer():
    col = lambda title, links: (f'<div><h5>{title}</h5><ul>'
                                + "".join(f'<li><a href="{h}">{e(n)}</a></li>' for n, h in links) + "</ul></div>")
    return (
        '<footer class="ft"><div class="wrap">'
        '<div class="ft-map">'
        f'<div><a class="logo" href="/"><b>{e(site["name_en"])}</b><span>{e(site["name"])}</span></a>'
        f'<p>{e(site["one_line"])}</p></div>'
        + col("회사", [("회사소개", "/#about"), ("수행실적", "/#projects"), ("문의하기", "/#contact")])
        + col("사업분야", [("정책 기획", "/business/policy/"), ("R&D 기획", "/business/rnd/"), ("조사분석", "/business/analysis/")])
        + col("연구개발", [("연구개발 개요", "/research/"), ("스마트팜", "/research/#smart-farm"), ("핵심 특허", "/research/#patent")])
        + col("자료", [("블로그", "/blog/"), ("RSS", "/blog/feed.xml")])
        + '</div><div class="ft-biz">'
        f'<span>{e(site["legal_name"])} · 대표이사 {e(site["ceo"])} · 사업자등록번호 {e(site["business_number"])} · {e(site["address"])} · '
        f'<a href="mailto:{e(site["email"])}">{e(site["email"])}</a></span>'
        f'<span>© {site["founded"]}–2026 {e(site["name_en"])} Inc.</span>'
        '</div></div></footer>'
    )


def head(title, desc, canonical, og_type="website", extra=""):
    return f"""<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<link rel="alternate" type="application/rss+xml" title="{e(site['name'])} 블로그" href="{BASE}/blog/feed.xml">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:site_name" content="{e(site['name'])}">
<meta property="og:locale" content="ko_KR">
{FONTS}{extra}"""


def ld(objs):
    return "\n".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in objs)


def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(items)]}
