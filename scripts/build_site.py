#!/usr/bin/env python3
"""홈과 사업·연구개발 페이지를 만듭니다.

만드는 것
  index.html                  홈 (4대 사업, 흐름, 연구개발 소개, 수행실적, 회사소개, 블로그, 문의)
  business/policy/index.html  정책 기획
  business/rnd/index.html     R&D 기획
  business/analysis/index.html 조사분석
  research/index.html         연구개발 (스마트팜)

회사 사실과 수행실적은 content/site.json에서 읽습니다. 끝나면 build_blog.py를 돌려
홈 <head>의 AEO 블록, 최신 글 목록, sitemap.xml, llms.txt를 채웁니다.
사용: python3 scripts/build_site.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout import ROOT, BASE, site, e, header, footer, head, ld, breadcrumb, FONTS  # noqa: E402
import iso  # noqa: E402

ORG_ID = BASE + "/#org"
AREA = {"policy": "정책 기획", "rnd": "R&D 기획", "analysis": "조사분석", "network": "네트워킹"}
TRACK = sorted(site["track"], key=lambda t: t[0], reverse=True)


def count(a):
    return sum(1 for t in TRACK if t[3] == a)


def clients(a=None):
    seen = []
    for t in TRACK:
        if (a is None or t[3] == a) and t[2] != "민간기업" and t[2] not in seen:
            seen.append(t[2])
    return seen


def track_rows(area=None):
    rows = []
    for y, name, client, a in TRACK:
        if area and a != area:
            continue
        rows.append(f'<tr data-area="{a}"><td class="y">{y}</td><td>{e(name)}</td>'
                    f'<td class="c">{e(client)}</td><td class="a"><span class="tag {a}">{AREA[a]}</span></td></tr>')
    return ('<table class="track"><thead><tr><th>연도</th><th>과제명</th><th class="c">발주기관</th><th>분야</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def loop_svg(ink, soft, accent, bg):
    """수요 예측 → 생산 계획 → 존별 재배 → 실적 피드백 도식"""
    box = lambda x, y, w, h, t, sub="": (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}" stroke="{soft}"/>'
        f'<text x="{x + 12}" y="{y + (h / 2) + (0 if sub else 5)}" font-size="13" fill="{ink}">{t}</text>'
        + (f'<text x="{x + 12}" y="{y + h / 2 + 17}" font-size="10" fill="{soft}" font-family="IBM Plex Mono,monospace">{sub}</text>' if sub else ""))
    arrow = lambda x1, y1, x2, y2: (f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{soft}" stroke-width="1.2" fill="none" marker-end="url(#ah)"/>')
    zones = "".join(
        f'<rect x="392" y="{48 + i * 62}" width="112" height="52" fill="{bg}" stroke="{accent if i == 1 else soft}"/>'
        f'<text x="402" y="{68 + i * 62}" font-size="10" fill="{accent}" font-family="IBM Plex Mono,monospace">ZONE {z}</text>'
        f'<text x="402" y="{87 + i * 62}" font-size="12.5" fill="{ink}">{n}</text>'
        for i, (z, n) in enumerate([("A", "엽채류"), ("B", "과채류"), ("C", "허브·약용")]))
    return f"""<svg viewBox="0 0 520 300" role="img" aria-label="수요처 주문과 시장·생육 데이터가 수요 예측 엔진으로 들어가 생산 계획이 되고, 세 개의 재배 존에서 생산한 실적이 다시 엔진으로 돌아가는 구조">
<defs><marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="{soft}" stroke-width="1.2"/></marker></defs>
<text x="16" y="24" font-size="10" fill="{soft}" font-family="IBM Plex Mono,monospace">INPUT</text>
<text x="200" y="24" font-size="10" fill="{soft}" font-family="IBM Plex Mono,monospace">ENGINE</text>
<text x="392" y="24" font-size="10" fill="{soft}" font-family="IBM Plex Mono,monospace">GREENBIO FARM</text>
{box(16, 48, 136, 52, "수요처 주문", "B2B ORDER")}
{box(16, 110, 136, 52, "시장·가격 데이터", "MARKET")}
{box(16, 172, 136, 52, "생육 데이터", "GROWTH")}
{arrow(152, 74, 196, 118)}{arrow(152, 136, 196, 136)}{arrow(152, 198, 196, 154)}
<rect x="200" y="96" width="140" height="80" fill="{bg}" stroke="{accent}" stroke-width="1.6"/>
<text x="214" y="130" font-size="14" fill="{ink}" font-weight="600">수요 예측 엔진</text>
<text x="214" y="152" font-size="10" fill="{soft}" font-family="IBM Plex Mono,monospace">FORECAST · MATCH</text>
{arrow(340, 136, 386, 136)}
<text x="344" y="126" font-size="10" fill="{soft}">계획</text>
{zones}
<path d="M448 234 L448 274 L270 274 L270 182" stroke="{soft}" stroke-width="1.2" stroke-dasharray="4 4" fill="none" marker-end="url(#ah)"/>
<text x="284" y="266" font-size="11" fill="{soft}">출하·생육 실적을 다시 학습</text>
</svg>"""


def contact_band():
    return f"""<section class="contact" id="contact"><div class="in"><div class="box">
<div><p class="eyebrow">문의하기</p>
<h2>과업지시서나 사업 개요가 있으면<br>먼저 보내 주세요</h2>
<p>자료를 읽고 수행 범위와 일정을 정리해 회신합니다. 스마트팜 연구개발 협력은 원물 제조업체, 스마트팜 농가, 지자체, 투자사 모두 문의할 수 있습니다.</p>
<a class="mail" href="mailto:{e(site['email'])}">{e(site['email'])} <span class="chev"></span></a></div>
<ol><li>메일로 과업 내용이나 협력 제안 접수</li><li>과업 범위와 일정 협의</li><li>수행계획서·견적 회신</li></ol>
</div></div></section>"""


def page(path, title, desc, body, current, jsonld, extra_head=""):
    out = ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
{head(title, desc, BASE + path, extra=extra_head)}
{ld(jsonld)}
</head>
<body>
{header(current)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
"""
    out.write_text(html, encoding="utf-8")


# ------------------------------------------------------------------ 홈
SLIDES = [
    ("policy", "s1", "01", "정책 기획", "지자체와 공공기관이 몇 년을 내다보고 움직일 수 있도록<br>목표, 추진과제, 성과지표를 갖춘 계획을 만듭니다.",
     [("주요 업무", "/business/policy/#scope"), ("수행실적", "/business/policy/#track")]),
    ("rnd", "s2", "02", "R&amp;D 기획", "정부 예산으로 추진할 신규 연구개발 사업의<br>필요성과 구조, 예산을 설계해 기획보고서로 정리합니다.",
     [("주요 업무", "/business/rnd/#scope"), ("진행 순서", "/business/rnd/#process")]),
    ("analysis", "s3", "03", "조사분석", "기술·특허 동향, 사전타당성, 입지와 기업 수요,<br>사업 성과까지 결정에 필요한 근거를 데이터로 확인합니다.",
     [("주요 업무", "/business/analysis/#scope"), ("수행실적", "/business/analysis/#track")]),
    ("research", "s4", "04", "연구개발 · 스마트팜", "한국전자기술연구원에서 기술이전받은 특허로<br>AI 수요 예측 스마트팜을 개발하고 실증합니다.",
     [("스마트팜 소개", "/research/#smart-farm"), ("핵심 특허", "/research/#patent")]),
]
QUICK_SUB = {"policy": "전략·계획 수립", "rnd": "신규사업 설계", "analysis": "근거 확인", "research": "스마트팜 개발"}


def card_icon(kind):
    """카드 오른쪽 위 작은 아이콘 (분야마다 모양이 다릅니다)"""
    body = {
        "policy": '<rect x="14" y="10" width="36" height="44" rx="6" fill="#EAF3FF"/><rect x="21" y="19" width="22" height="4" rx="2" fill="#126BDA"/><rect x="21" y="28" width="18" height="3" rx="1.5" fill="#9DBCEB"/><rect x="21" y="35" width="20" height="3" rx="1.5" fill="#9DBCEB"/><path d="M22 45 l4 4 l9 -10" fill="none" stroke="#1E9E5A" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
        "rnd": '<rect x="8" y="40" width="12" height="14" rx="3" fill="#C8D4FA"/><rect x="24" y="30" width="12" height="24" rx="3" fill="#8FA6EE"/><rect x="40" y="18" width="12" height="36" rx="3" fill="#5B4FD0"/><path d="M46 18 v-10 l10 3 l-10 3" fill="#FF8A3D"/>',
        "analysis": '<circle cx="28" cy="28" r="16" fill="#E0F6F8" stroke="#0E8A9A" stroke-width="4"/><path d="M40 40 l12 12" stroke="#0E8A9A" stroke-width="6" stroke-linecap="round"/><path d="M20 32 l5 -6 l5 4 l7 -9" fill="none" stroke="#126BDA" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
    }[kind]
    return f'<svg class="ico" viewBox="0 0 64 64" aria-hidden="true">{body}</svg>'


def build_home():
    n_all = len(TRACK)
    n_cli = len(clients())

    slides = "".join(
        f'<div class="slide {cls}{" on" if i == 0 else ""}" role="group" aria-roledescription="slide" aria-label="{i + 1} / 4">'
        f'<div><span class="num">{no}</span><h2>{title}</h2><p>{desc}</p><div class="pills">'
        + "".join(f'<a class="pill" href="{h}">{n} <span class="chev"></span></a>' for n, h in btns)
        + f'</div></div><div class="art">{iso.SCENES[key]()}</div></div>'
        for i, (key, cls, no, title, desc, btns) in enumerate(SLIDES))
    dots = "".join(f'<button type="button" class="{"on" if i == 0 else ""}" aria-label="{i + 1}번 슬라이드"></button>' for i in range(4))
    quick = "".join(
        f'<a href="{SLIDES[i][5][0][1].split("#")[0]}" data-i="{i}"{" class=on" if i == 0 else ""}><b>{SLIDES[i][2]}</b><span>{SLIDES[i][3].split(" · ")[0]}<small>{QUICK_SUB[SLIDES[i][0]]}</small></span></a>'
        for i in range(4))

    track_list = "".join(
        f'<li><a href="/business/{a}/#track" ><span class="badge {"blue" if a == "policy" else "navy"}">{AREA[a]}</span><b>{e(n)}</b><time>{y}</time></a></li>'
        if a != "network" else
        f'<li><a href="/business/analysis/#related"><span class="badge">{AREA[a]}</span><b>{e(n)}</b><time>{y}</time></a></li>'
        for y, n, c, a in TRACK[:5])

    def card(key, name, path):
        rows = [t for t in TRACK if t[3] == key]
        cl = clients(key)
        years = sorted({t[0] for t in rows})
        tags = "".join(f'<span class="hash">#{e(c.replace(" ", ""))}</span>' for c in cl[:4])
        return (f'<a class="card" href="{path}"><div class="top"><div class="bdg"><span class="badge out">{years[0]}–{years[-1][2:]}</span>'
                f'<span><span class="badge red">공공</span><span class="badge blue">{len(rows)}건</span></span></div>'
                f'<h3>{name}</h3>{card_icon(key)}<div>{tags}</div></div>'
                f'<ul class="stats"><li><span>수행 과제</span><b>{len(rows)}<small>건</small></b></li>'
                f'<li><span>발주기관</span><b>{len(cl)}<small>곳</small></b></li>'
                f'<li><span>최근 과제</span><em class="t">{e(rows[0][1])}</em></li></ul>'
                f'<span class="more">자세히 보기</span></a>')

    clients_all = clients()
    marquee = "".join(f"<li>{e(c)}</li>" for c in clients_all) * 2

    body = f"""
<section class="visual" aria-label="사업분야 소개"><div class="in">
<div class="slides" id="slides">{slides}</div>
<div class="slider-ctrl"><div class="dots" id="dots">{dots}<button type="button" class="pause" id="pause" aria-label="자동 넘김 멈춤">❚❚</button></div></div>
<nav class="quick" id="quick" aria-label="사업분야 바로가기">{quick}</nav>
</div></section>

<section id="areas"><div class="in news-grid">
<div class="notice-board">
<div class="sec-head"><h2 class="h-sec"><span class="blue">이노베리움</span> 소식</h2>
<div class="tabs" role="tablist"><button type="button" role="tab" aria-selected="true" aria-controls="tb-blog" id="t-blog"><span class="ck"></span>블로그</button>
<button type="button" role="tab" aria-selected="false" aria-controls="tb-track" id="t-track"><span class="ck"></span>수행실적</button></div>
<a class="plus" id="plus" href="/blog/" aria-label="소식 더보기"></a></div>
<div class="board" id="tb-blog" role="tabpanel" aria-labelledby="t-blog"><!-- BLOG:LATEST START --><!-- BLOG:LATEST END --></div>
<div class="board" id="tb-track" role="tabpanel" aria-labelledby="t-track" hidden><ul>{track_list}</ul></div>
</div>
<div>
<div class="sec-head"><h2 class="h-sec">알림판</h2><div class="bn-ctrl" style="margin-left:auto"><button type="button" id="bnPrev" aria-label="이전">◀</button><span><b id="bnNo">01</b> / 03</span><button type="button" id="bnNext" aria-label="다음">▶</button></div></div>
<div class="banner" id="banner">
<div class="bn b1 on"><small>수행실적</small><h3>설립 첫해부터<br>공공 과제 {n_all}건</h3><p>공공 발주기관 {n_cli}곳과 정책·R&amp;D 기획, 조사분석 과제를 수행했습니다.</p><div class="big">{n_all}<small>건</small></div><a class="go" href="/about/#projects" aria-label="수행실적 보기"><span class="chev"></span></a></div>
<div class="bn b2"><small>연구개발</small><h3>고령군 그린바이오 수직농장<br>실증 테스트 진행 중</h3><p>기술이전 특허를 적용한 다품종 정밀환경 그린바이오팜을 실증하고 있습니다.</p><div class="big">2027<small>상용화 목표</small></div><a class="go" href="/research/#roadmap" aria-label="로드맵 보기"><span class="chev"></span></a></div>
<div class="bn b3"><small>블로그</small><h3>R&amp;D 기획 실무 질문에<br>답하는 글을 올립니다</h3><p>예타 사전기획, 성과지표, 기술이전 절차처럼 현장에서 자주 받는 질문을 다룹니다.</p><div class="big">Q&amp;A</div><a class="go" href="/blog/" aria-label="블로그 보기"><span class="chev"></span></a></div>
</div></div>
</div></section>

<section class="cards-sec"><div class="in">
<div class="center"><h2 class="h-sec">사업분야별 <span class="blue">수행실적</span></h2>
<p class="lede">정책 기획, R&amp;D 기획, 조사분석으로 나눠 본 {site['founded']}년 이후 공공 과제입니다.</p></div>
<div class="cards">{card("policy", "정책 기획", "/business/policy/")}{card("rnd", "R&amp;D 기획", "/business/rnd/")}{card("analysis", "조사분석", "/business/analysis/")}</div>
<p class="center" style="margin-top:30px"><a class="btn line" href="/about/#projects">전체 수행실적 보기 <span class="chev"></span></a></p>
</div></section>

<section style="padding-top:20px"><div class="in"><div class="rd-band">
<div><p class="eyebrow" style="color:#C9F5D8">연구개발 · 스마트팜</p>
<h2>스마트팜 기술을 함께 실증할<br>파트너를 찾고 있습니다</h2>
<p>수요를 먼저 예측하고 그에 맞춰 품목과 물량을 정하는 스마트팜을 개발하고 있습니다. 원물 제조업체, 농가, 지자체, 투자사의 협력 제안을 받습니다.</p>
<a class="btn" href="/research/">연구개발 전체보기 <span class="chev"></span></a></div>
<div class="rd-cards">
<div class="rd-card"><p class="tags">#소프트웨어 #AI</p><h3>AI 수요 예측 엔진</h3><dl><dt>기능</dt><dd>수요 예측, 생산능력 분석, 수요·공급 매칭</dd><dt>목표</dt><dd>수요 예측 오차(MAPE) 15% 이하</dd></dl></div>
<div class="rd-card"><p class="tags">#하드웨어 #기술이전</p><h3>다품종 정밀환경 그린바이오팜</h3><dl><dt>구성</dt><dd>엽채류·과채류·허브 3개 독립 존</dd><dt>기반</dt><dd>특허 제10-2407262호 (한국전자기술연구원)</dd></dl></div>
</div></div></div></section>

<section class="clients" aria-label="주요 발주기관"><div class="in">
<h2>주요 발주기관 <button type="button" id="mqBtn" aria-label="흐름 멈춤">❚❚</button></h2>
<div class="marquee" id="mq"><ul>{marquee}</ul></div>
</div></section>

{contact_band()}

<script>
(function(){{
  var sl=[].slice.call(document.querySelectorAll('#slides .slide')),dt=[].slice.call(document.querySelectorAll('#dots button:not(.pause)')),
      qk=[].slice.call(document.querySelectorAll('#quick a')),cur=0,run=true,t;
  function go(i){{cur=(i+sl.length)%sl.length;sl.forEach(function(s,k){{s.classList.toggle('on',k===cur)}});
    dt.forEach(function(d,k){{d.classList.toggle('on',k===cur)}});qk.forEach(function(q,k){{q.classList.toggle('on',k===cur)}});}}
  function loop(){{clearInterval(t);if(run)t=setInterval(function(){{go(cur+1)}},5500)}}
  dt.forEach(function(d,k){{d.onclick=function(){{go(k);loop()}}}});
  qk.forEach(function(q,k){{q.onmouseenter=function(){{go(k)}}}});
  var p=document.getElementById('pause');p.onclick=function(){{run=!run;p.textContent=run?'❚❚':'▶';p.setAttribute('aria-label',run?'자동 넘김 멈춤':'자동 넘김 시작');loop()}};
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches)loop();else{{run=false;p.textContent='▶'}}
  var tabs=[].slice.call(document.querySelectorAll('.tabs [role=tab]')),plus=document.getElementById('plus');
  tabs.forEach(function(b){{b.onclick=function(){{tabs.forEach(function(x){{x.setAttribute('aria-selected',x===b);document.getElementById(x.getAttribute('aria-controls')).hidden=(x!==b)}});
    plus.href=b.id==='t-blog'?'/blog/':'/about/#projects';}}}});
  if(document.querySelectorAll('#tb-blog li').length<3)document.getElementById('t-track').click();
  var bn=[].slice.call(document.querySelectorAll('#banner .bn')),bi=0,no=document.getElementById('bnNo');
  function bgo(i){{bi=(i+bn.length)%bn.length;bn.forEach(function(x,k){{x.classList.toggle('on',k===bi)}});no.textContent='0'+(bi+1)}}
  document.getElementById('bnPrev').onclick=function(){{bgo(bi-1)}};document.getElementById('bnNext').onclick=function(){{bgo(bi+1)}};
  var mq=document.getElementById('mq'),mb=document.getElementById('mqBtn');
  mb.onclick=function(){{mq.classList.toggle('paused');var ps=mq.classList.contains('paused');mb.textContent=ps?'▶':'❚❚';mb.setAttribute('aria-label',ps?'흐름 시작':'흐름 멈춤')}};
}})();
</script>"""

    title = f"{site['name']} | 정책 기획 · R&D 기획 · 조사분석 · 연구개발"
    desc = f"{site['name']}은 {site['one_line']}입니다. 수행실적 {n_all}건, 공공 발주기관 {n_cli}곳."
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="naver-site-verification" content="0c45c9d8db9fc7784ad7843c1879d776f16e13c1" />
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
{FONTS}
<!-- AEO:HEAD START --><!-- AEO:HEAD END -->
</head>
<body>
{header("home")}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")


# ------------------------------------------------------------------ 회사소개
def build_about():
    n_all = len(TRACK)
    story = "".join(f"<p>{e(s)}</p>" for s in site["story"])
    filters = "".join(f'<button type="button" data-f="{k}" aria-pressed="false">{v}</button>' for k, v in AREA.items())
    body = f"""
<section class="ph"><div class="in">
<div class="art">{iso.policy()}</div>
<div class="crumb"><a href="/">홈</a><span>회사소개</span></div>
<p class="eyebrow">About</p>
<h1>회사소개</h1>
<p class="answer"><strong>{e(site['name'])}은 {e(site['one_line'])}입니다.</strong> {site['founded']}년에 설립했고, 지금까지 공공 과제 {n_all}건을 수행했습니다.</p>
<nav class="sib" aria-label="회사소개"><a href="/about/" aria-current="page">회사 개요</a><a href="#projects">수행실적</a><a href="#team">조직·인력</a><a href="#location">오시는 길</a></nav>
</div></section>

<section><div class="in overview">
<div><h2 class="h-sec" style="margin-bottom:18px">혁신이 있는 공간, <span class="blue">이노베리움</span></h2>{story}
<p>공공 용역 외에 기업·투자자·기관이 만나는 네트워킹 행사를 운영하고, 6가지 질문으로 제품과 사업계획을 시장 관점에서 점검하는 소비자 Deep Dive 워크숍도 진행합니다.</p></div>
<table class="info"><tbody>
<tr><th>회사명</th><td>{e(site['legal_name'])} ({e(site['name_en'])})</td></tr>
<tr><th>대표이사</th><td>{e(site['ceo'])}</td></tr>
<tr><th>설립</th><td>{site['founded']}년</td></tr>
<tr><th>업종</th><td>전문 과학 및 기술서비스업</td></tr>
<tr><th>사업분야</th><td>정책 기획 · R&amp;D 기획 · 조사분석 · 연구개발(스마트팜)</td></tr>
<tr><th>사업자등록번호</th><td>{e(site['business_number'])}</td></tr>
<tr><th>문의</th><td><a class="more-link" href="mailto:{e(site['email'])}">{e(site['email'])}</a></td></tr>
</tbody></table>
</div></section>

<section class="rule" id="projects"><div class="in">
<h2 class="h-sec">수행실적</h2>
<p class="lede">공공기관은 기관명을 적고, 민간기업은 이름을 밝히지 않습니다.</p>
<div class="filters" role="group" aria-label="분야별 보기"><button type="button" data-f="all" aria-pressed="true">전체 {n_all}</button>{filters}</div>
{track_rows()}
</div></section>

<section class="rule" id="team"><div class="in">
<h2 class="h-sec">조직·인력</h2>
<p class="lede">연구인력 4명(박사 1명, 석사 2명 포함)이 일하고, 기술개발실을 운영합니다.</p>
<div style="margin-top:30px"><div class="org-top">대표이사</div>
<div class="org"><div><b>자문위원단</b><p>분야별 외부 전문가 자문, 기획 내용 검토</p></div>
<div><b>기획연구팀</b><p>정책·R&amp;D 기획, 조사분석 과제 수행</p></div>
<div><b>행정연구팀</b><p>과제 행정, 성과 관리, 기술개발실 지원</p></div></div></div>
</div></section>

<section class="rule" id="location"><div class="in">
<h2 class="h-sec" style="margin-bottom:24px">오시는 길</h2>
<div class="map"><span class="pin"><svg width="28" height="28" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z" fill="#fff"/></svg></span>
<div><b>{e(site['address'])}</b><p>대전광역시 유성구 · 문의 {e(site['email'])}</p></div></div>
</div></section>

{contact_band()}

<script>
(function(){{
  var bs=document.querySelectorAll('.filters button'),rows=document.querySelectorAll('.track tbody tr');
  bs.forEach(function(b){{b.addEventListener('click',function(){{
    var f=b.dataset.f;bs.forEach(function(x){{x.setAttribute('aria-pressed',x===b)}});
    rows.forEach(function(r){{r.style.display=(f==='all'||r.dataset.area===f)?'':'none'}});
  }})}});
}})();
</script>"""
    jsonld = [breadcrumb([("홈", "/"), ("회사소개", "/about/")]),
              {"@context": "https://schema.org", "@type": "AboutPage", "url": BASE + "/about/", "name": f"{site['name']} 회사소개",
               "about": {"@type": "Organization", "@id": ORG_ID, "name": site["name"]}}]
    page("/about/", f"회사소개 | {site['name']}", f"{site['name']} 회사 개요, 수행실적 {n_all}건, 조직·인력, 오시는 길.", body, "about", jsonld)


# ------------------------------------------------------------------ 사업 페이지
SIB = [("policy", "정책 기획", "/business/policy/"), ("rnd", "R&D 기획", "/business/rnd/"),
       ("analysis", "조사분석", "/business/analysis/"), ("research", "연구개발", "/research/")]


def sib(cur):
    return '<nav class="sib" aria-label="사업분야">' + "".join(
        f'<a href="{h}"{" aria-current=page" if k == cur else ""}>{n}</a>' for k, n, h in SIB) + "</nav>"


def faq_html(faq):
    return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq) + "</div>"


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def biz_page(key, path, name, en, answer_strong, answer_rest, work, steps, faq, extra=""):
    work_rows = "".join(f"<tr><th>{e(a)}</th><td>{e(b)}</td><td class=\"o\">{e(c)}</td></tr>" for a, b, c in work)
    step_rows = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in steps)
    n = count(key)
    cli = clients(key)
    body = f"""
<section class="ph"><div class="in">
<div class="art">{iso.SCENES[key]()}</div>
<div class="crumb"><a href="/">홈</a><a href="/#areas">사업분야</a><span>{e(name)}</span></div>
<p class="eyebrow">{en}</p>
<h1>{e(name)}</h1>
<p class="answer"><strong>{e(answer_strong)}</strong> {e(answer_rest)}</p>
{sib(key)}
</div></section>

<section id="scope"><div class="wrap two"><header><p class="eyebrow">Scope</p><h2>주요 업무</h2></header>
<table class="work"><thead><tr><th>업무</th><th>내용</th><th>주요 산출물</th></tr></thead><tbody>{work_rows}</tbody></table>
</div></section>

<section class="rule" id="process"><div class="wrap two"><header><p class="eyebrow">Process</p><h2>진행 순서</h2></header>
<ol class="steps">{step_rows}</ol>
</div></section>

<section class="rule" id="track"><div class="wrap two"><header><p class="eyebrow">Track record</p><h2>{e(name)} 수행실적</h2>
<p class="note">{n}건 · 발주기관 {e(" · ".join(cli))}</p></header>
<div>{track_rows(key)}<p class="note">전체 실적은 <a class="more-link" href="/about/#projects">회사소개 › 수행실적</a>에서 볼 수 있습니다.</p></div>
</div></section>
{extra}
<section class="rule"><div class="wrap two"><header><p class="eyebrow">FAQ</p><h2>자주 묻는 질문</h2></header>
{faq_html(faq)}
</div></section>

{contact_band()}"""
    url = BASE + path
    jsonld = [
        {"@context": "https://schema.org", "@type": "Service", "@id": url + "#service", "name": name,
         "serviceType": name, "description": answer_strong + " " + answer_rest, "url": url,
         "provider": {"@type": "Organization", "@id": ORG_ID, "name": site["name"], "url": BASE + "/"},
         "areaServed": {"@type": "Country", "name": "대한민국"},
         "hasOfferCatalog": {"@type": "OfferCatalog", "name": name + " 업무", "itemListElement": [
             {"@type": "Offer", "itemOffered": {"@type": "Service", "name": a, "description": b}} for a, b, _ in work]}},
        breadcrumb([("홈", "/"), (name, path)]),
        faq_ld(faq),
    ]
    page(path, f"{name} | {site['name']}", f"{answer_strong} {answer_rest}"[:155], body, key, jsonld)


def build_policy():
    biz_page(
        "policy", "/business/policy/", "정책 기획", "Policy planning",
        "정책 기획은 정부·지자체·공공기관이 풀어야 할 산업·기술 과제를 정하고, 목표와 추진과제, 예산, 성과지표를 갖춘 계획으로 만드는 일입니다.",
        "이노베리움은 지역 산업육성 발전전략, 연구기관의 R&D 전략계획, 성과관리 체계를 설계합니다.",
        [("지역 산업육성 발전전략", "지역 산업 현황과 데이터·인프라 기반을 진단하고, 육성 분야와 추진과제, 단계별 일정을 정합니다.", "발전전략 보고서, 추진과제 로드맵"),
         ("기관 R&D 전략계획", "연구기관의 중장기 연구 방향을 정하고 고유사업과 신규사업의 배치를 정리합니다.", "전략계획서, 연구분야 체계도"),
         ("성과관리 체계 재정립", "기존 성과지표를 점검하고 사업 목표에 맞는 지표, 목표치, 점검 주기를 다시 세웁니다.", "성과지표 정의서, 성과관리 지침"),
         ("조직 실행체계 설계", "업무 지식을 자산으로 정리하고, AI 도구를 업무에 쓰는 절차와 역할을 설계합니다.", "실행체계 설계서")],
        [("과업 확인", "과업지시서와 기존 계획, 상위 정책을 읽고 과업 범위를 확정합니다."),
         ("현황 진단", "통계·예산·기존 사업 실적을 모으고 담당 부서와 외부 전문가를 인터뷰합니다."),
         ("과제 정의", "진단 결과에서 정책이 풀어야 할 문제를 몇 개로 좁힙니다."),
         ("비전·목표", "기간별 목표와 측정할 수 있는 목표치를 정합니다."),
         ("추진과제·재원", "과제별 내용, 담당, 일정, 소요 예산을 정리합니다."),
         ("성과관리·보고", "성과지표와 점검 방법을 정하고 최종 보고서로 묶습니다.")],
        [("정책 기획과 R&D 기획은 어떻게 다른가요?", "정책 기획은 기관이나 지역 전체가 갈 방향과 추진과제를 정합니다. R&D 기획은 그 추진과제 가운데 연구개발 예산으로 할 사업 하나를 구체적으로 설계합니다."),
         ("어떤 기관이 정책 기획을 맡기나요?", "지금까지는 지자체 산하 진흥원과 국립 연구기관이 주로 맡겼습니다. 대전정보문화산업진흥원과 국립수목원 과제가 그 예입니다."),
         ("의뢰하기 전에 무엇을 준비하면 되나요?", "과업지시서나 사업 개요, 기관의 기존 계획과 성과 자료가 있으면 범위를 빨리 정할 수 있습니다. 자료가 없으면 첫 협의에서 함께 정리합니다."),
         ("성과지표만 따로 맡길 수 있나요?", "맡길 수 있습니다. 국립수목원 과제처럼 R&D 전략계획 가운데 성과관리 체계 재정립만 따로 수행한 사례가 있습니다.")])


def build_rnd():
    biz_page(
        "rnd", "/business/rnd/", "R&D 기획", "R&D program planning",
        "R&D 기획은 정부 연구개발 예산으로 추진할 신규 사업의 필요성, 목표, 연구 내용, 추진체계, 예산을 설계해 기획보고서로 만드는 일입니다.",
        "이노베리움은 신규 R&D 사업의 사전기획과 기획요소 도출, 연구 인프라·데이터 구축 기획을 수행합니다.",
        [("신규 R&D 사업 기획", "사업 필요성과 목표를 세우고 내역사업, 세부 과제, 연차별 예산을 짭니다.", "신규사업 기획보고서"),
         ("사전기획·기획요소 도출", "본기획에 앞서 연구 수요와 기술 동향을 조사해 사업 후보와 핵심 기획요소를 뽑습니다.", "사전기획 보고서, 후보 과제 목록"),
         ("연구 인프라·데이터 구축 기획", "연구에 쓸 데이터셋, 라이브러리, 장비의 구축 범위와 운영 방식을 설계합니다.", "구축 기획서, 운영 방안"),
         ("기술로드맵(TRM)", "목표 기술을 세부 기술로 나누고 확보 시점과 확보 방법을 정합니다.", "기술 트리, 단계별 로드맵")],
        [("수요·동향 조사", "연구 현장과 수요기관 의견, 국내외 기술·정책 동향을 모읍니다."),
         ("기획요소 도출", "사업이 다룰 문제, 목표 기술, 대상 분야를 정합니다."),
         ("사업 구조 설계", "목표와 내역사업, 세부 과제가 어떻게 이어지는지 짭니다."),
         ("추진체계·예산", "수행 주체와 기간, 연차별 예산을 정합니다."),
         ("성과지표·파급효과", "성과지표와 목표치, 기대 효과를 정리합니다."),
         ("기획보고서·검토 대응", "보고서를 쓰고 자문회의와 검토 의견에 맞춰 고칩니다.")],
        [("사전기획과 본기획은 어떻게 다른가요?", "사전기획은 사업을 할지, 한다면 어떤 방향으로 할지를 정하는 앞 단계입니다. 본기획은 그 방향에 맞춰 과제 구성과 예산까지 확정하는 단계입니다."),
         ("어떤 분야의 R&D 사업을 기획했나요?", "산림 탄소중립 기반구축, 수목원 고유 연구, 피지컬 AI 라이브러리 구축 분야의 사업을 기획했습니다."),
         ("기획보고서에는 무엇이 들어가나요?", "추진 배경과 필요성, 국내외 동향, 목표와 사업 구조, 추진체계, 예산, 성과지표와 기대효과가 들어갑니다."),
         ("기술 분야가 낯설어도 맡길 수 있나요?", "맡길 수 있습니다. 기획 과정에서 해당 분야 연구자와 자문위원단 의견을 받아 기술 내용을 채웁니다.")])


def build_analysis():
    extra = """
<section class="rule" id="related"><div class="wrap two"><header><p class="eyebrow">Related</p><h2>연계 업무</h2></header>
<table class="work"><tbody>
<tr><th>네트워킹·투자연계</th><td>기업, 투자자, 기관이 만나는 협력 행사를 기획하고 운영합니다. 충북대학교기술지주의 C-LOVE Investment Networking Day를 운영했습니다.</td><td class="o">행사 운영, 결과 보고</td></tr>
<tr><th>소비자 Deep Dive 워크숍</th><td>6가지 핵심 질문으로 제품과 사업계획을 시장과 소비자 관점에서 점검합니다.</td><td class="o">워크숍 결과지</td></tr>
</tbody></table>
</div></section>"""
    biz_page(
        "analysis", "/business/analysis/", "조사분석", "Research & analysis",
        "조사분석은 정책이나 사업을 결정하기 전에 기술, 시장, 입지, 성과를 자료와 데이터로 확인하는 일입니다.",
        "이노베리움은 기술·특허 동향 분석, 사전타당성 검토, 입지분석과 기업 수요조사, 사업 효과성·성과분석을 수행합니다.",
        [("기술 동향 분석", "논문·특허·정책 자료로 기술 수준과 연구 주체, 상용화 단계를 정리합니다.", "기술 동향 보고서"),
         ("핵심 특허 확보 전략", "대상 기술의 특허 지형을 분석하고 확보할 특허와 회피 설계 방향을 정합니다.", "특허 분석 보고서, IP 확보 전략"),
         ("사전타당성 검토", "기관 설립이나 시설 건립의 필요성, 수요, 입지, 재원, 운영 방안을 따집니다.", "사전타당성 보고서"),
         ("입지분석·기업 수요조사", "후보지 여건을 비교하고 설문과 인터뷰로 기업 수요를 확인합니다.", "입지 평가표, 수요조사 결과"),
         ("효과성·성과분석", "사업이 낸 성과를 집계하고, 목표한 변화가 실제로 나타났는지 따집니다.", "성과분석 보고서, 개선 과제")],
        [("질문 정하기", "이번 조사로 무엇을 결정할지 발주기관과 먼저 정합니다."),
         ("자료 설계", "필요한 통계, 논문·특허 데이터, 설문 문항, 인터뷰 대상을 정합니다."),
         ("수집", "데이터베이스 검색, 설문, 현장 방문, 인터뷰로 자료를 모읍니다."),
         ("분석", "정량 분석 결과를 비교표, 지도, 도표로 정리합니다."),
         ("해석·시사점", "결과가 결정에 주는 의미와 남은 불확실성을 함께 적습니다.")],
        [("효과성 분석과 성과분석은 어떻게 다른가요?", "성과분석은 사업이 만든 논문, 특허, 사업화 같은 결과를 집계하고 평가합니다. 효과성 분석은 그 결과가 사업이 목표한 변화로 이어졌는지를 따집니다."),
         ("사전타당성 검토에서는 무엇을 보나요?", "설립이나 건립이 필요한 이유, 수요, 입지, 재원 조달, 운영 방식을 봅니다. 전북특별자치도 완주군의 한국수소산업진흥원 설립 검토가 그 예입니다."),
         ("기업 수요조사는 어떻게 하나요?", "조사 목적에 맞는 기업 명단을 만들고 설문과 심층 인터뷰를 함께 씁니다. 결과는 입지 선정과 지원 정책 설계에 바로 쓸 수 있게 정리합니다."),
         ("조사 결과를 기획까지 이어서 맡길 수 있나요?", "맡길 수 있습니다. 이노베리움은 정책 기획과 R&D 기획도 하므로 조사 결과를 바탕으로 다음 단계 기획을 이어서 수행합니다.")],
        extra)


# ------------------------------------------------------------------ 연구개발
def build_research():
    faq = [("이노베리움 스마트팜은 일반 스마트팜과 무엇이 다른가요?", "재배 전에 AI로 수요를 예측해 품목과 물량을 정하고, 독립된 존에서 여러 품목을 동시에 키웁니다. 수요가 바뀌면 48시간 안에 품목을 바꾸는 것을 목표로 합니다."),
           ("어떤 특허를 기반으로 하나요?", "한국전자기술연구원의 특허 제10-2407262호 '열전달 특성이 반영된 균일난방 제어 장치 및 방법'을 기술이전받았습니다."),
           ("실증은 어디에서 하나요?", "고령군 그린바이오 수직농장에서 실증 테스트를 하고 있습니다."),
           ("어떤 협력을 찾고 있나요?", "원물을 쓰는 제조업체, 스마트팜 농가, 지자체, 투자사와의 협력을 찾고 있습니다. 메일로 협력 내용을 보내 주시면 회신합니다.")]
    kpi = [("≤15%", "수요 예측 오차 (MAPE)"), ("30%↓", "과잉 생산"), ("40%↓", "물 사용량"),
           ("20%↑", "에너지 효율"), ("48h", "품목 전환 시간"), ("30%↑", "농가 소득")]
    road = [("2026 H1", "기술 내재화·제품화 개발", "특허 기술 교육과 노하우 이전, 그린바이오팜 설계 검토, 프로토타입 개발", ""),
            ("2026 H2", "실증 테스트", "고령군 그린바이오 수직농장 실증, 시험성적서 확보, 시스템 안정화", ""),
            ("2027 Q2", "상용화 출시", "그린바이오팜과 수요 예측 엔진 출시, B2B 원물 공급 계약", "목표 매출 35억 원"),
            ("2028", "K-스마트팜 패키지 B2B", "하드웨어와 AI 수급 조절 소프트웨어 패키지 납품, 스마트팜 혁신밸리 확산", "목표 매출 65억 원"),
            ("2029", "SaaS·해외 진출", "수요 예측 엔진 SaaS 적용 확대, K-스마트팜 패키지 수출 모델 개발", "목표 매출 105억 원")]
    body = f"""
<section class="ph rd-hero"><div class="in">
<div class="art">{iso.research()}</div>
<div class="crumb"><a href="/">홈</a><span>연구개발</span></div>
<p class="eyebrow">In-house R&amp;D</p>
<h1>연구개발</h1>
<p class="answer"><strong>이노베리움은 공공기관 용역과 별도로, 기술이전받은 특허를 바탕으로 스마트팜 기술을 직접 연구개발합니다.</strong> 지금은 AI 수요 예측 엔진과 다품종 정밀환경 그린바이오팜을 개발하고, 고령군 그린바이오 수직농장에서 실증하고 있습니다.</p>
{sib("research")}
</div></section>

<section id="smart-farm"><div class="wrap">
<p class="eyebrow">연구 분야 01</p>
<h2 class="h-sec">스마트팜 <span class="status">개발 진행 중</span></h2>
<p class="lede">수요를 먼저 예측하고 그에 맞춰 품목과 물량을 정하는 수요 반응형 스마트팜입니다. 소프트웨어(수요 예측 엔진)와 하드웨어(그린바이오팜)를 함께 개발합니다.</p>
<nav class="inner-nav" aria-label="스마트팜 목차"><a href="#problem">문제 인식</a><a href="#develop">개발 내용</a><a href="#patent">핵심 특허</a><a href="#kpi">목표 지표</a><a href="#roadmap">로드맵</a></nav>
</div></section>

<section class="rule" id="problem"><div class="wrap">
<p class="eyebrow">Problem</p><h2 class="h-sec">지금 스마트팜이 겪는 문제</h2>
<p class="lede">국내 스마트팜은 시설 면적이 늘었지만 구조적인 문제가 남아 있습니다.</p>
<div class="prob" style="margin-top:30px">
<div><h4>과잉 공급과 가격 하락</h4><p>딸기·토마토·파프리카 같은 소수 품목에 생산이 몰려, 같은 품목 생산량이 늘면 값이 떨어질 우려가 있습니다.</p></div>
<div><h4>높은 초기비용</h4><p>비닐하우스 기반 스마트팜도 초기비용이 20~30억 원이 들고, 에너지 가격 상승이 경제성을 떨어뜨립니다.</p></div>
<div><h4>영세농가 부담</h4><p>수급 조절과 가격 보장 없이 시설이 모이면 관행 농가의 입지가 좁아지고, 대기업 자본 진출 우려도 나옵니다.</p></div>
<div><h4>생육 데이터 부족</h4><p>파프리카를 빼면 국산 품목의 체계화된 생육 데이터가 적어 AI를 적용할 기반이 약합니다.</p></div>
</div></div></section>

<section class="rule" id="develop"><div class="wrap">
<p class="eyebrow">Development</p><h2 class="h-sec">두 가지를 함께 개발합니다</h2>
<div class="engine">
<div><p class="eyebrow">Demand engine</p><h3>AI 수요 예측 엔진</h3>
<p>공급 가능 물량과 수요처 주문량을 맞춰 품목별 생산 계획을 세우는 소프트웨어입니다.</p>
<ul><li>수요 예측 <code>Transformer + LSTM</code></li><li>생산능력 분석 <code>CNN + 생육정보</code></li><li>수요·공급 매칭 <code>GNN + NSGA-II</code></li><li>디지털 트윈 시뮬레이션으로 생산 계획을 미리 검증</li></ul></div>
<figure class="fig">{loop_svg("#121212", "#7C8BA3", "#126BDA", "#F5F9FF")}<figcaption>FIG.1 수요 예측에서 생산, 실적 피드백까지</figcaption></figure>
</div>
<div class="engine g">
<div><p class="eyebrow">GreenBio farm</p><h3>다품종 정밀환경 그린바이오팜</h3>
<p>독립된 환경 존(Zone)에서 여러 품목을 동시에 키우고, 수요 예측 엔진의 계획에 맞춰 품목을 바꾸는 재배 시설입니다.</p>
<ul><li>엽채류·과채류·허브/약용 3개 독립 존</li><li>존마다 온도·습도·광·CO₂를 따로 제어</li><li>양액 EC·pH·DO 실시간 모니터링</li><li>수직 다단 랙으로 면적당 생산량 최대 3배 목표</li></ul></div>
<figure class="fig"><table class="zones"><thead><tr><th>존</th><th>대상 품목</th><th>온도</th><th>재배 구성</th></tr></thead><tbody>
<tr><td><b>A</b> · 엽채류</td><td>상추, 케일, 청경채</td><td>18~22°C</td><td>8~12단, 연 17모작</td></tr>
<tr><td><b>B</b> · 과채류</td><td>딸기, 토마토, 파프리카</td><td>22~28°C</td><td>4~6단, 풀스펙트럼 광</td></tr>
<tr><td><b>C</b> · 허브·약용</td><td>바질, 민트, 로즈마리</td><td>20~25°C</td><td>6~10단, UV-A 처리</td></tr>
</tbody></table><figcaption>FIG.2 존별 재배 조건 (설계 기준)</figcaption></figure>
</div></div></section>

<section class="rule" id="patent"><div class="wrap">
<p class="eyebrow">Core patent</p><h2 class="h-sec">기술이전받은 핵심 특허</h2>
<div class="patent" style="margin-top:24px">
<div><h3>열전달 특성이 반영된<br>균일난방 제어 장치 및 방법</h3>
<p class="no">특허 제10-2407262호 · 한국전자기술연구원</p>
<p>자연대류와 강제대류의 열전달 계수를 반영해 재배시설 안을 고르게 난방하는 기술입니다. 온도 편차를 줄여 병해충 발생을 막고 에너지 사용량을 낮춥니다.</p>
<p>이노베리움은 이 특허를 다품종 정밀 환경제어에 맞게 고쳐 그린바이오팜에 적용하고, 고령군 그린바이오 수직농장에서 실증하고 있습니다.</p></div>
<table class="spec"><tbody>
<tr><th>온도 편차 제어</th><td>±0.3~0.5°C 유지</td></tr>
<tr><th>열전달 모델링</th><td>자연대류 + 강제대류 통합</td></tr>
<tr><th>배관 설계</th><td>구역별 배치, 수온 자동 제어</td></tr>
<tr><th>병해충 예방</th><td>온도 편차 관리로 발생 조건 차단</td></tr>
<tr><th>에너지 효율</th><td>생산량당 전력(kWh/kg) 20% 개선 목표</td></tr>
</tbody></table>
</div></div></section>

<section class="rule" id="kpi"><div class="wrap">
<p class="eyebrow">Targets</p><h2 class="h-sec">목표 성과지표</h2>
<p class="lede">개발 목표치입니다. 실증 결과가 나오면 측정값으로 바꿔 적습니다.</p>
<div class="kpi">{"".join(f"<div><b>{v}</b><span>{e(l)}</span></div>" for v, l in kpi)}</div>
</div></section>

<section class="rule" id="roadmap"><div class="wrap two"><header><p class="eyebrow">Roadmap</p><h2>상용화 로드맵</h2></header>
<ol class="road">{"".join(f"<li><time>{t}</time><div><b>{e(a)}</b><span>{e(b)}</span></div><em>{e(c)}</em></li>" for t, a, b, c in road)}</ol>
</div></section>

<section class="rule"><div class="wrap">
<p class="eyebrow">Capability</p><h2 class="h-sec">연구 기반</h2>
<div class="lab" style="margin-top:26px">
<div><b>연구 인력</b><p>연구인력 4명(박사 1명, 석사 2명 포함), 기술개발실 운영</p></div>
<div><b>기술이전</b><p>한국전자기술연구원 스마트 농업 특허 기술이전, 공공 연구기관 협력</p></div>
<div><b>산업 분석</b><p>그린바이오 밸류체인 기업 분석과 데이터 가공. 조사분석 사업에서 쌓은 방법을 연구개발에 씁니다.</p></div>
</div></div></section>

<section class="rule"><div class="wrap two"><header><p class="eyebrow">FAQ</p><h2>자주 묻는 질문</h2></header>
{faq_html(faq)}
</div></section>

{contact_band()}"""
    url = BASE + "/research/"
    jsonld = [
        {"@context": "https://schema.org", "@type": "ResearchProject", "@id": url + "#smart-farm",
         "name": "AI 수요 예측 기반 다품종 정밀환경 그린바이오팜 개발", "url": url + "#smart-farm",
         "description": "기술이전받은 균일난방 제어 특허(제10-2407262호)를 바탕으로 AI 수요 예측 엔진과 다품종 정밀환경 그린바이오팜을 개발하고 고령군 그린바이오 수직농장에서 실증하는 연구개발",
         "parentOrganization": {"@type": "Organization", "@id": ORG_ID, "name": site["name"]},
         "keywords": "스마트팜, 그린바이오, 수직농장, 수요 예측, 정밀 환경제어, 기술이전"},
        breadcrumb([("홈", "/"), ("연구개발", "/research/")]),
        faq_ld(faq),
    ]
    page("/research/", f"연구개발 · 스마트팜 | {site['name']}",
         "이노베리움은 한국전자기술연구원에서 기술이전받은 특허로 AI 수요 예측 엔진과 다품종 정밀환경 그린바이오팜을 개발하고, 고령군 그린바이오 수직농장에서 실증합니다.",
         body, "research", jsonld)


def main():
    build_home()
    build_about()
    build_policy()
    build_rnd()
    build_analysis()
    build_research()
    import build_blog
    build_blog.main()
    print("페이지 6개 빌드 완료")


if __name__ == "__main__":
    main()
