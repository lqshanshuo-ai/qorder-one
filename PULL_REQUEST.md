## Summary
- Build a full-stack content creator automation platform (FastAPI + Next.js)
- Implement end-to-end workflow: multi-source crawling (Weibo, Zhihu, Baidu, arXiv) → AI topic selection → DingDing confirmation → content research & script generation → text+image montage video production → publishing preparation
- Add web dashboard for topic management, pipeline control, video gallery, and analytics

## Test plan
- [ ] Verify backend starts: `cd backend && PYTHONPATH=. uvicorn app.main:app --reload`
- [ ] Verify frontend starts: `cd frontend && npm run dev`
- [ ] Test crawl endpoint: `POST /api/crawl/run`
- [ ] Test topic CRUD: `GET /api/topics/`
- [ ] Test pipeline trigger: `POST /api/topics/{id}/generate`
- [ ] Confirm DingDing notification callback works with configured webhook
- [ ] Verify video generation outputs to `output/` directory

---
**Branch:** `qoder/content-creation-platform-jQvMD3`
**Base:** `main`

### To create this PR manually:
```bash
git push --set-upstream origin qoder/content-creation-platform-jQvMD3
gh pr create --title "feat: content creator automation platform" --body-file PULL_REQUEST.md --base main
```
