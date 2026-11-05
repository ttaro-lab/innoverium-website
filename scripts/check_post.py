#!/usr/bin/env python3
"""블로그 글 JSON을 AEO 기준과 문체 기준으로 점검합니다.

사용: python3 scripts/check_post.py content/posts/2026-11-09-xxx.json [--forbid 단어1,단어2]
      (--forbid 대신 환경변수 AEO_FORBID 도 됩니다. 이 목록은 저장소에 넣지 않습니다.)
FAIL이 하나라도 있으면 종료 코드 1.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STOCK = ["혁신적인", "혁신적으로", "획기적", "최고의", "다양한", "효과적으로", "핵심적인 역할", "시너지", "나아가",
         "더불어", "살펴보겠습니다", "알아보겠습니다", "알아볼까요", "결론적으로", "요약하자면", "무엇보다",
         "필수적입니다", "중요합니다", "도약", "선도하는", "선도적", "새로운 지평", "패러다임", "한 단계 더",
         "극대화", "원스톱", "솔루션을 제공", "최적의", "차별화된", "노하우를 바탕으로", "풍부한 경험",
         "전문성을 바탕으로", "하는 것이 중요", "라고 할 수 있습니다", "가 아닐까", "미래를 열", "함께 성장", "—", "!"]
REQUIRED = ["slug", "date", "type", "title", "meta_description", "lead", "summary", "sections", "faq", "tags"]


def all_text(p):
    parts = [p.get("title"), p.get("lead"), *p.get("summary", [])]
    for s in p.get("sections", []):
        parts += [s.get("h2"), s.get("answer"), *s.get("body", []), *s.get("list", [])]
        for r in (s.get("table") or {}).get("rows", []):
            parts += r
    for q in p.get("faq", []):
        parts += [q.get("q"), q.get("a")]
    return "\n".join(str(x) for x in parts if x)


def check(path, forbid):
    p = json.loads(Path(path).read_text(encoding="utf-8"))
    res = []
    ok = lambda c, lvl, msg: res.append(("OK" if c else lvl, msg))

    missing = [k for k in REQUIRED if not p.get(k)]
    ok(not missing, "FAIL", f"필수 항목 {'없음: ' + ', '.join(missing) if missing else '모두 있음'}")
    ok(re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", p.get("slug", "")) is not None, "FAIL", f"slug 형식 (영소문자-숫자-하이픈): {p.get('slug')}")
    ok(re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.get("date", "")) is not None, "FAIL", f"date 형식 YYYY-MM-DD: {p.get('date')}")
    txt = all_text(p)

    ok(bool(re.search(r"\?|나요|가요|까요|무엇|어떻게", p.get("title", ""))), "FAIL", "제목이 질문형")
    ok(len(p.get("lead", "")) <= 130, "WARN", f"정의문 길이 {len(p.get('lead', ''))}자 (130자 이하)")
    ok(len(p.get("summary", [])) == 3, "FAIL", f"핵심 요약 {len(p.get('summary', []))}줄 (3줄)")
    secs = p.get("sections", [])
    ok(4 <= len(secs) <= 8, "FAIL", f"H2 섹션 {len(secs)}개 (4~8개)")
    bad_ans = [s.get("h2") for s in secs if not s.get("answer") or len(s["answer"]) > 90]
    ok(not bad_ans, "FAIL", "섹션 첫 직답 90자 이하" + (f" — 고칠 곳: {bad_ans}" if bad_ans else ""))
    tables = sum(1 for s in secs if (s.get("table") or {}).get("rows"))
    ok(tables >= 1, "FAIL", f"표 {tables}개 (최소 1개)")
    ok(tables >= 2, "WARN", "표 2개 이상 권장")
    ok(len(p.get("faq", [])) >= 5, "FAIL", f"FAQ {len(p.get('faq', []))}개 (5개 이상)")
    ml = len(p.get("meta_description", ""))
    ok(80 <= ml <= 160, "WARN", f"메타 설명 {ml}자 (80~160자)")
    if p.get("type") == "trend":
        ok(len(p.get("sources", [])) >= 2, "FAIL", "동향 글은 참고 자료 2개 이상")
    for s in p.get("sources", []):
        ok(str(s.get("url", "")).startswith("http"), "FAIL", f"참고 자료 URL: {s.get('title')}")

    chk = re.findall(r"\[확인 필요[^\]]*\]", txt)
    ok(not chk, "FAIL", "[확인 필요] 표시 없음" + (f" — {len(chk)}곳 남음" if chk else ""))
    hits = [w for w in STOCK if w in txt]
    ok(len(hits) <= 1, "FAIL", "상투어·AI 말투" + (f" — {', '.join(hits)}" if hits else " 없음"))
    leak = [w for w in forbid if w and w.lower() in txt.lower()]
    ok(not leak, "FAIL", "금지어 노출" + (f" — {', '.join(leak)}" if leak else " 없음"))

    sents = [s for s in re.split(r"(?<=[.다요])\s+|\n", txt) if len(s.strip()) > 8]
    if sents:
        L = [len(s) for s in sents]
        avg = sum(L) / len(L)
        cv = (sum((x - avg) ** 2 for x in L) / len(L)) ** 0.5 / avg
        ok(cv >= 0.35, "WARN", f"문장 길이 편차 {cv:.2f} (0.35 이상이면 덜 기계적)")
    starts = [s.get("answer", "")[:4] for s in secs]
    ok(len(starts) == len(set(starts)), "WARN", "섹션 직답 첫머리 반복 없음")

    # 기존 글과 제목이 너무 비슷한지
    words = set(re.findall(r"[가-힣A-Za-z0-9]{2,}", p.get("title", "")))
    for f in (ROOT / "content" / "posts").glob("*.json"):
        if f.resolve() == Path(path).resolve():
            continue
        o = json.loads(f.read_text(encoding="utf-8"))
        ow = set(re.findall(r"[가-힣A-Za-z0-9]{2,}", o.get("title", "")))
        if words and len(words & ow) / len(words | ow) > 0.6:
            res.append(("FAIL", f"기존 글과 제목이 거의 같음: {o.get('title')}"))
        if o.get("slug") == p.get("slug"):
            res.append(("FAIL", f"slug 중복: {f.name}"))
    return res


def main():
    args = sys.argv[1:]
    forbid = [w.strip() for w in os.environ.get("AEO_FORBID", "").split(",")]
    if "--forbid" in args:
        i = args.index("--forbid")
        forbid += [w.strip() for w in args[i + 1].split(",")]
        del args[i:i + 2]
    if not args:
        sys.exit(__doc__)
    failed = False
    for path in args:
        print(f"== {path}")
        for lvl, msg in check(path, forbid):
            print(f"  [{lvl}] {msg}")
            failed |= lvl == "FAIL"
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
