# innoverium-website
이노베리움 공식 홈페이지 (Vercel 정적 배포)

## 사이트 구조
| 주소 | 내용 |
|---|---|
| `/` | 홈: 4대 사업, 연구개발 소개, 수행실적, 회사소개, 최신 블로그, 문의 |
| `/business/policy/` | 정책 기획 |
| `/business/rnd/` | R&D 기획 |
| `/business/analysis/` | 조사분석 |
| `/research/` | 연구개발 › 스마트팜 (`#smart-farm`) |
| `/blog/` | 블로그 |

- 메뉴·푸터 사이트맵: `scripts/layout.py`의 `MENU`, `PAGES`
- 페이지 본문: `scripts/build_site.py` · 공통 스타일: `assets/site.css`
- 회사 정보·수행실적: `content/site.json` (`track`의 네 번째 값이 분야: policy / rnd / analysis / network)
- 페이지 빌드: `python3 scripts/build_site.py` (끝에 블로그 빌드까지 함께 돌립니다)
- 연구개발 분야를 추가하려면 `build_research()`에 `연구 분야 02` 섹션을 넣고 `MENU`의 연구개발 하위메뉴에 한 줄 추가합니다.

## 블로그
- 글 원본: `content/posts/*.json` · 회사 정보: `content/site.json` · 주제 목록: `content/topics.json`
- 작성 지침: `AUTHORING.md`
- 점검: `python3 scripts/check_post.py content/posts/<파일>.json`
- 빌드: `python3 scripts/build_blog.py` → `blog/`, `sitemap.xml`, `robots.txt`, `llms.txt`, 홈 `<head>` AEO 블록 갱신
- 새 글은 PR로 올리고, 병합하면 배포됩니다.
