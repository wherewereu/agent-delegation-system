# HEARTBEAT.md — website-agent-hosting

## My Mission
Own the /agent-hosting page. Keep it accurate, fast, and production-ready.

## Weekly Checks
1. Verify https://flumeusa.com/agent-hosting returns 200
2. Check all 6 features present with correct names
3. Verify pricing matches /pricing page (Free $0, Lite $19, Pro $39)
4. Check all CTAs link to working URLs (/signup, /signup/?plan=...)
5. Mobile layout — all sections readable on 375px
6. No placeholder text or outdated content
7. Check social proof stats (127+, 99.9%, 3 min, 94%)

## Pre-deploy Checklist
- [ ] All 6 features shown correctly
- [ ] Pricing matches /pricing page exactly
- [ ] Stats are current (127+ agents, 99.9% uptime)
- [ ] All links resolve (no dead hrefs)
- [ ] Mobile responsive — test at 375px
- [ ] Dark theme: bg #0a0a0f, accent #ff6b00
- [ ] Build: `npm run build` passes
- [ ] Tests: `npm test -- --run` passes

## If Issues Found
- Fix and commit immediately for small issues
- Spawn Builder for structural changes
- Redeploy: `wrangler pages deploy out/ --project-name=flume --branch=main`

## Key Files
- `/Users/soup/flume/app/agent-hosting/page.tsx`
- `/Users/soup/flume/app/agent-hosting/__tests__/page.test.tsx`
- `/Users/soup/flume/agent-hosting/CONTENT.md` (source content)
