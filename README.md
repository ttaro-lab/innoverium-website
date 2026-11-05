# innoverium-website
이노베리움 공식 홈페이지 (Vercel 정적 배포)

## 블로그
- 글 원본: `content/posts/*.json` · 회사 정보: `content/site.json` · 주제 목록: `content/topics.json`
- 작성 지침: `AUTHORING.md`
- 점검: `python3 scripts/check_post.py content/posts/<파일>.json`
- 빌드: `python3 scripts/build_blog.py` → `blog/`, `sitemap.xml`, `robots.txt`, `llms.txt`, 홈 `<head>` AEO 블록 갱신
- 새 글은 PR로 올리고, 병합하면 배포됩니다.
