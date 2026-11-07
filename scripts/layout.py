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


# (키, 이름, 주소, 하위메뉴[(이름, 주소)]) · 메가메뉴와 모바일 메뉴가 이 목록으로 그려집니다
MENU = [
    ("about", "회사소개", "/about/", [("회사 개요", "/about/"), ("수행실적", "/about/#projects"), ("조직·인력", "/about/#team"), ("오시는 길", "/about/#location")]),
    ("policy", "정책 기획", "/business/policy/", [("주요 업무", "/business/policy/#scope"), ("진행 순서", "/business/policy/#process"), ("수행실적", "/business/policy/#track")]),
    ("rnd", "R&D 기획", "/business/rnd/", [("주요 업무", "/business/rnd/#scope"), ("진행 순서", "/business/rnd/#process"), ("수행실적", "/business/rnd/#track")]),
    ("analysis", "조사분석", "/business/analysis/", [("주요 업무", "/business/analysis/#scope"), ("진행 순서", "/business/analysis/#process"), ("수행실적", "/business/analysis/#track"), ("연계 업무", "/business/analysis/#related")]),
    ("research", "연구개발", "/research/", [("스마트팜", "/research/#smart-farm"), ("개발 내용", "/research/#develop"), ("핵심 특허", "/research/#patent"), ("상용화 로드맵", "/research/#roadmap")]),
    ("news", "알림마당", "/blog/", [("블로그", "/blog/"), ("문의하기", "/#contact")]),
]

# 사이트 전체 페이지 목록 (sitemap.xml, llms.txt에 씁니다)
PAGES = [
    ("/", "홈", "정책 기획, R&D 기획, 조사분석, 연구개발 소개와 최신 소식"),
    ("/about/", "회사소개", "회사 개요, 수행실적 전체, 조직·인력, 오시는 길"),
    ("/business/policy/", "정책 기획", "지역 산업육성 전략, 기관 R&D 전략계획, 성과관리 체계 설계"),
    ("/business/rnd/", "R&D 기획", "신규 R&D 사업 사전기획·본기획, 기획요소 도출, 연구 인프라 구축 기획"),
    ("/business/analysis/", "조사분석", "기술·특허 동향, 사전타당성, 입지분석·수요조사, 효과성·성과분석"),
    ("/research/", "연구개발 · 스마트팜", "기술이전 특허 기반 AI 수요 예측 엔진과 다품종 정밀환경 그린바이오팜"),
]

FONTS = (
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">\n'
    '<link rel="stylesheet" href="/assets/site.css">'
)


def header(current=""):
    top, mega = [], []
    for key, name, href, subs in MENU:
        cur = ' aria-current="page"' if key == current else ""
        sub = "".join(f'<li><a href="{h}">{e(n)}</a></li>' for n, h in subs)
        top.append(f'<li class="d1{" on" if cur else ""}"><a href="{href}"{cur}>{e(name)}</a><ul class="d2">{sub}</ul></li>')
    return (
        '<a class="skip" href="#main">본문 바로가기</a>\n'
        '<div class="util"><div class="in"><a href="/blog/">블로그</a><a href="/#contact">문의하기</a></div></div>\n'
        '<header class="hd"><div class="in">'
        f'<a class="logo" href="/" aria-label="{e(site["name"])} 홈">{LOGO}<span><b>{e(site["name"])}</b><small>{e(site["name_en"])}</small></span></a>'
        f'<nav class="gnb" id="gnb" aria-label="주메뉴"><ul>{"".join(top)}</ul></nav>'
        '<button class="menu-btn" aria-label="전체메뉴" aria-expanded="false" aria-controls="gnb" '
        "onclick=\"var h=document.querySelector('.hd');h.classList.toggle('open');this.setAttribute('aria-expanded',h.classList.contains('open'))\">"
        '<i></i><i></i><i></i></button>'
        '</div><div class="mega-bg"></div></header>'
    )


# 잎 두 장과 온실 지붕선을 합친 로고 기호
LOGO = ('<svg class="mark" viewBox="0 0 40 40" aria-hidden="true">'
        '<rect x="1" y="1" width="38" height="38" rx="11" fill="#126BDA"/>'
        '<path d="M9 27 L20 12 L31 27" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>'
        '<path d="M20 30 C14 30 12 25 13 21 C17 21 20 24 20 30Z" fill="#7DDB8A"/>'
        '<path d="M20 30 C26 30 28 25 27 21 C23 21 20 24 20 30Z" fill="#C6F0A8"/></svg>')


def footer():
    links = "".join(f'<option value="{h}">{e(n)}</option>' for _, n, h, _ in MENU)
    return (
        '<footer class="ft"><div class="in">'
        '<div class="ft-top">'
        '<ul class="ft-links"><li><a href="/about/">회사소개</a></li><li><a href="/about/#location">오시는 길</a></li>'
        '<li><a href="/blog/feed.xml">RSS</a></li><li><a href="/#contact">문의하기</a></li></ul>'
        '<label class="ft-sel"><span class="skip">사업분야 바로가기</span>'
        f'<select onchange="if(this.value)location.href=this.value"><option value="">사업분야 바로가기</option>{links}</select></label>'
        '</div>'
        f'<div class="ft-brand">{LOGO}<b>{e(site["name"])}</b></div>'
        f'<address>{e(site["address"])} · 대표이사 {e(site["ceo"])} · 사업자등록번호 {e(site["business_number"])}<br>'
        f'문의 <a href="mailto:{e(site["email"])}">{e(site["email"])}</a></address>'
        f'<p class="copy">Copyright © 2026 {e(site["legal_name"])}. All Rights Reserved.</p>'
        '</div></footer>'
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
