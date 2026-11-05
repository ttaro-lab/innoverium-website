#!/usr/bin/env python3
"""content/posts/*.json 을 읽어 정적 블로그를 만듭니다.

만드는 것
  blog/index.html            글 목록
  blog/<slug>/index.html     글 페이지 (BlogPosting·FAQPage·BreadcrumbList JSON-LD 포함)
  blog/feed.xml              RSS
  sitemap.xml, robots.txt, llms.txt
  index.html <head> 의 AEO 블록 (canonical, OG, Organization JSON-LD)

외부 패키지 없이 python3 표준 라이브러리만 씁니다.
사용: python3 scripts/build_blog.py
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
POSTS = CONTENT / "posts"
BLOG = ROOT / "blog"

site = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
BASE = site["url"].rstrip("/")
ORG_ID = BASE + "/#org"

TYPE_LABEL = {
    "brand": "회사 소개", "define": "용어 정리", "howto": "절차·방법",
    "guide": "준비 가이드", "trend": "동향", "case": "수행 사례",
}


def e(s):
    return html.escape(str(s or ""), quote=True)


def load_posts():
    posts = []
    for f in sorted(POSTS.glob("*.json")):
        p = json.loads(f.read_text(encoding="utf-8"))
        p["_file"] = f.name
        posts.append(p)
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    slugs = [p["slug"] for p in posts]
    dup = {s for s in slugs if slugs.count(s) > 1}
    if dup:
        sys.exit(f"slug 중복: {', '.join(dup)}")
    return posts


def kdate(d):
    y, m, dd = d.split("-")
    return f"{y}년 {int(m)}월 {int(dd)}일"


def reading_minutes(p):
    text = " ".join([p.get("lead", "")] + [" ".join(s.get("body", [])) + s.get("answer", "") for s in p["sections"]]
                    + [q["q"] + q["a"] for q in p.get("faq", [])])
    return max(2, round(len(text) / 600))


STYLE = """
:root{--bg:#0A0F0D;--card:#111A15;--line:rgba(255,255,255,.08);--text:#E3EAE5;--dim:#93A89B;--bright:#fff;
--green:#2ECC71;--green-soft:rgba(46,204,113,.14);--mark:rgba(46,204,113,.28);
--display:'Outfit','Noto Sans KR',sans-serif;--body:'Noto Sans KR',sans-serif;--tech:'Space Grotesk',monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:var(--body);line-height:1.8;font-size:17px}
a{color:var(--green)}
.bar{border-bottom:1px solid var(--line);background:var(--bg);position:sticky;top:0;z-index:5}
.bar-in{max-width:1080px;margin:0 auto;padding:14px max(20px,env(safe-area-inset-left));display:flex;justify-content:space-between;align-items:center;gap:16px}
.logo{font-family:var(--display);font-weight:800;font-size:1.3rem;color:var(--bright);text-decoration:none;letter-spacing:-.5px}
.logo span{font-weight:400;font-size:.7rem;color:var(--dim);margin-left:6px;letter-spacing:2px}
.bar nav a{color:var(--dim);text-decoration:none;font-size:.9rem;margin-left:18px}
.bar nav a:hover,.bar nav a[aria-current]{color:var(--green)}
main{max-width:760px;margin:0 auto;padding:48px max(20px,env(safe-area-inset-left)) 80px}
.crumb{font-size:.82rem;color:var(--dim);margin-bottom:18px}
.crumb a{color:var(--dim);text-decoration:none}
.kind{font-family:var(--tech);font-size:.72rem;letter-spacing:3px;color:var(--green);text-transform:uppercase}
h1{font-family:var(--display);font-size:clamp(1.7rem,4vw,2.4rem);line-height:1.35;color:var(--bright);margin:10px 0 14px;font-weight:700;text-wrap:balance}
.meta{font-size:.85rem;color:var(--dim);margin-bottom:28px}
.lead{font-size:1.12rem;color:var(--bright);margin-bottom:24px}
.lead strong,.ans strong{background:linear-gradient(transparent 60%,var(--mark) 60%);font-weight:600}
.sum{border:1px solid rgba(46,204,113,.35);background:var(--green-soft);border-radius:4px;padding:18px 22px;margin:28px 0 8px}
.sum b{display:block;font-family:var(--tech);font-size:.72rem;letter-spacing:3px;color:var(--green);margin-bottom:8px}
.sum ol{padding-left:20px}.sum li{margin:2px 0}
h2{font-family:var(--display);font-size:1.4rem;color:var(--bright);margin:48px 0 12px;line-height:1.45;text-wrap:balance}
h3{font-size:1.06rem;color:var(--bright);margin:26px 0 6px}
p{margin:0 0 14px}
ul.list{margin:0 0 16px 20px}
.tbl{overflow-x:auto;margin:14px 0 22px}
table{border-collapse:collapse;width:100%;min-width:460px;font-size:.93rem}
caption{caption-side:top;text-align:left;color:var(--dim);font-size:.82rem;padding-bottom:6px}
th,td{border:1px solid var(--line);padding:9px 12px;text-align:left;vertical-align:top}
th{background:var(--card);color:var(--bright);font-weight:500}
.src{font-size:.9rem;color:var(--dim)}.src li{margin:4px 0 4px 18px}
.cta{margin:48px 0 0;padding:26px;border:1px solid var(--line);background:var(--card);border-radius:4px}
.cta p{color:var(--dim);margin-bottom:6px}
.cta .mail{font-family:var(--tech);color:var(--bright);font-size:1.05rem}
.tags{margin-top:26px;font-size:.85rem;color:var(--dim)}
.more{margin-top:48px;border-top:1px solid var(--line);padding-top:22px}
.more h2{margin-top:0;font-size:1.1rem}
.more a{display:block;color:var(--text);text-decoration:none;padding:8px 0;border-bottom:1px solid var(--line)}
.more a:hover{color:var(--green)}
.posts{list-style:none}
.posts li{border-bottom:1px solid var(--line);padding:22px 0}
.posts a{text-decoration:none;color:var(--bright);font-size:1.18rem;font-weight:500;line-height:1.5;display:block;margin:4px 0 6px}
.posts a:hover{color:var(--green)}
.posts p{color:var(--dim);font-size:.95rem;margin:0}
.posts time{font-family:var(--tech);font-size:.78rem;color:var(--dim);margin-left:8px}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:.82rem}
footer div{max-width:1080px;margin:0 auto;padding:22px max(20px,env(safe-area-inset-left))}
@media (max-width:520px){body{font-size:16px}.bar nav a{margin-left:12px}}
"""

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Space+Grotesk:wght@500;700&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">'


def shell(title, desc, canonical, body, jsonld, og_type="article", current=""):
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in jsonld)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
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
{FONTS}
<style>{STYLE}</style>
{ld}
</head>
<body>
<header class="bar"><div class="bar-in">
<a class="logo" href="/">{e(site['name_en'])}<span>{e(site['name'])}</span></a>
<nav><a href="/">회사 소개</a><a href="/blog/"{' aria-current="page"' if current=='blog' else ''}>블로그</a><a href="/#contact">문의</a></nav>
</div></header>
{body}
<footer><div>{e(site['legal_name'])} · 대표 {e(site['ceo'])} · 사업자등록번호 {e(site['business_number'])} · {e(site['address'])} · {e(site['email'])}</div></footer>
</body>
</html>
"""


def org_ld():
    return {
        "@context": "https://schema.org", "@type": "Organization", "@id": ORG_ID,
        "name": site["name"], "alternateName": site["name_en"], "legalName": site["legal_name"],
        "url": BASE + "/", "email": site["email"], "foundingDate": site["founded"],
        "founder": {"@type": "Person", "name": site["ceo"]},
        "description": f"{site['name']}은 {site['one_line']}입니다.",
        "address": {"@type": "PostalAddress", "addressCountry": "KR", "addressRegion": "대전광역시",
                    "addressLocality": site["locality"], "streetAddress": site["address"]},
        "taxID": site["business_number"],
        "knowsAbout": site["sectors"],
    }


def render_table(t):
    if not t or not t.get("rows"):
        return ""
    cap = f"<caption>{e(t.get('caption'))}</caption>" if t.get("caption") else ""
    head = "".join(f"<th>{e(h)}</th>" for h in t.get("headers", []))
    rows = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in t["rows"])
    return f'<div class="tbl"><table>{cap}<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def render_post(p, others):
    url = f"{BASE}/blog/{p['slug']}/"
    out = [f'<main><article>',
           f'<div class="crumb"><a href="/">홈</a> › <a href="/blog/">블로그</a></div>',
           f'<div class="kind">{e(TYPE_LABEL.get(p.get("type"), "블로그"))}</div>',
           f'<h1>{e(p["title"])}</h1>',
           f'<div class="meta"><time datetime="{p["date"]}">{kdate(p["date"])}</time>'
           + (f' · 수정 <time datetime="{p["updated"]}">{kdate(p["updated"])}</time>' if p.get("updated") else "")
           + f' · {reading_minutes(p)}분 읽기 · {e(site["name"])}</div>',
           f'<p class="lead"><strong>{e(p["lead"])}</strong></p>']
    if p.get("summary"):
        out.append('<div class="sum"><b>핵심 요약</b><ol>' + "".join(f"<li>{e(s)}</li>" for s in p["summary"]) + "</ol></div>")
    for s in p["sections"]:
        out.append(f'<h2>{e(s["h2"])}</h2>')
        if s.get("answer"):
            out.append(f'<p class="ans"><strong>{e(s["answer"])}</strong></p>')
        out += [f"<p>{e(x)}</p>" for x in s.get("body", [])]
        out.append(render_table(s.get("table")))
        if s.get("list"):
            out.append('<ul class="list">' + "".join(f"<li>{e(x)}</li>" for x in s["list"]) + "</ul>")
    if p.get("faq"):
        out.append("<h2>자주 묻는 질문</h2>")
        for q in p["faq"]:
            out.append(f"<h3>{e(q['q'])}</h3><p>{e(q['a'])}</p>")
    if p.get("sources"):
        out.append('<h2>참고 자료</h2><ul class="src">')
        for s in p["sources"]:
            extra = " · ".join(x for x in [s.get("publisher"), s.get("date")] if x)
            out.append(f'<li><a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s["title"])}</a>{" · " + e(extra) if extra else ""}</li>')
        out.append("</ul>")
    out.append(f'<div class="cta"><p>{e(site["name"])}에 R&D 기획·컨설팅을 문의하려면</p><a class="mail" href="mailto:{e(site["email"])}">{e(site["email"])}</a></div>')
    if p.get("tags"):
        out.append('<div class="tags">' + " ".join("#" + e(t.replace(" ", "")) for t in p["tags"]) + "</div>")
    if others:
        out.append('<nav class="more"><h2>다른 글</h2>' + "".join(f'<a href="/blog/{o["slug"]}/">{e(o["title"])}</a>' for o in others) + "</nav>")
    out.append("</article></main>")

    ld = [
        org_ld(),
        {"@context": "https://schema.org", "@type": "BlogPosting", "@id": url + "#post", "mainEntityOfPage": url,
         "headline": p["title"][:110], "description": p["meta_description"], "datePublished": p["date"],
         "dateModified": p.get("updated", p["date"]), "inLanguage": "ko-KR",
         "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "keywords": ", ".join(p.get("tags", [])),
         "citation": [s["url"] for s in p.get("sources", [])] or None},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "블로그", "item": BASE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"][:60], "item": url}]},
    ]
    if p.get("faq"):
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in p["faq"]]})
    for x in ld:
        for k in [k for k, v in x.items() if v is None]:
            del x[k]
    return shell(p["title"], p["meta_description"], url, "\n".join(o for o in out if o), ld)


def render_index(posts):
    items = "".join(
        f'<li><span class="kind">{e(TYPE_LABEL.get(p.get("type"), ""))}</span><time datetime="{p["date"]}">{p["date"].replace("-", ".")}</time>'
        f'<a href="/blog/{p["slug"]}/">{e(p["title"])}</a><p>{e(p["lead"])}</p></li>' for p in posts)
    desc = f"{site['name']} 블로그. 정책·R&D 기획, 산업 컨설팅, 기술·특허 분석, 그린바이오 스마트팜에 관한 질문에 답합니다."
    body = f'<main><div class="kind">BLOG</div><h1>{e(site["name"])} 블로그</h1><p class="meta">{e(desc)}</p><ul class="posts">{items}</ul></main>'
    ld = [org_ld(), {"@context": "https://schema.org", "@type": "Blog", "@id": BASE + "/blog/#blog", "name": f"{site['name']} 블로그",
                     "url": BASE + "/blog/", "publisher": {"@id": ORG_ID}, "inLanguage": "ko-KR",
                     "blogPost": [{"@type": "BlogPosting", "headline": p["title"][:110], "url": f"{BASE}/blog/{p['slug']}/", "datePublished": p["date"]} for p in posts]}]
    return shell(f"{site['name']} 블로그", desc, BASE + "/blog/", body, ld, og_type="website", current="blog")


def render_feed(posts):
    items = "".join(
        f"<item><title>{e(p['title'])}</title><link>{BASE}/blog/{p['slug']}/</link><guid>{BASE}/blog/{p['slug']}/</guid>"
        f"<pubDate>{date.fromisoformat(p['date']).strftime('%a, %d %b %Y')} 09:00:00 +0900</pubDate><description>{e(p['meta_description'])}</description></item>"
        for p in posts[:30])
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>{e(site["name"])} 블로그</title>'
            f'<link>{BASE}/blog/</link><description>{e(site["one_line"])}</description><language>ko</language>{items}</channel></rss>\n')


def render_sitemap(posts):
    today = date.today().isoformat()
    urls = [(BASE + "/", today), (BASE + "/blog/", posts[0]["date"] if posts else today)]
    urls += [(f"{BASE}/blog/{p['slug']}/", p.get("updated", p["date"])) for p in posts]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n'


def render_llms(posts):
    lines = [f"# {site['name']} ({site['legal_name']})", "", f"> {site['name']}은 {site['one_line']}입니다.", "",
             f"- 대표: {site['ceo']}", f"- 설립: {site['founded']}년", f"- 소재지: {site['address']}", f"- 문의: {site['email']}", "",
             "## 하는 일", *[f"- {s}" for s in site["services"]], "", "## 블로그 글",
             *[f"- [{p['title']}]({BASE}/blog/{p['slug']}/): {p['lead']}" for p in posts], ""]
    return "\n".join(lines)


HEAD_START, HEAD_END = "<!-- AEO:HEAD START -->", "<!-- AEO:HEAD END -->"


def update_home():
    f = ROOT / "index.html"
    s = f.read_text(encoding="utf-8")
    block = (f'{HEAD_START}\n<link rel="canonical" href="{BASE}/">\n'
             f'<link rel="alternate" type="application/rss+xml" title="{e(site["name"])} 블로그" href="{BASE}/blog/feed.xml">\n'
             f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="{e(site["name"])}">\n'
             f'<meta property="og:url" content="{BASE}/">\n<meta property="og:locale" content="ko_KR">\n'
             f'<script type="application/ld+json">{json.dumps(org_ld(), ensure_ascii=False)}</script>\n{HEAD_END}')
    if HEAD_START in s:
        s = re.sub(re.escape(HEAD_START) + r".*?" + re.escape(HEAD_END), lambda m: block, s, flags=re.S)
    else:
        s = s.replace("</head>", block + "\n</head>", 1)
    f.write_text(s, encoding="utf-8")


def main():
    posts = load_posts()
    BLOG.mkdir(exist_ok=True)
    for i, p in enumerate(posts):
        others = [o for o in posts if o is not p][:4]
        d = BLOG / p["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(render_post(p, others), encoding="utf-8")
    (BLOG / "index.html").write_text(render_index(posts), encoding="utf-8")
    (BLOG / "feed.xml").write_text(render_feed(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(render_sitemap(posts), encoding="utf-8")
    (ROOT / "llms.txt").write_text(render_llms(posts), encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    update_home()
    print(f"글 {len(posts)}편 빌드 완료")


if __name__ == "__main__":
    main()
