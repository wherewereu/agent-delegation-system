# HEARTBEAT.md — website-homepage

## My Mission
Keep the Flume homepage production-ready at all times.

## Weekly Checks (run every heartbeat)
1. Verify https://flumeusa.com returns 200 and loads correctly
2. Verify all 3 product cards are present and link to correct URLs
3. Check for any console errors or broken resources
4. Verify mobile layout (test with narrow viewport)
5. Check that /agent-hosting, /pricing links resolve (200)
6. Report any dead links, broken redirects, or outdated content

## If I find issues
- Small fix (typo, CSS, broken link): Fix and commit immediately
- Large fix (missing page, structural change): Spawn Builder agent with specific task
- Always push to main and redeploy via `wrangler pages deploy out/ --project-name=flume --branch=main`

## Pre-deploy Checklist (before any homepage change)
- [ ] All 3 products shown with correct names, badges, hrefs
- [ ] No dead nav links
- [ ] Mobile responsive (test at 375px width)
- [ ] No placeholder text ("lorem ipsum", "coming soon", "TBD")
- [ ] Dark theme consistent (#0a0a0f bg, #ff6b00 accent)
- [ ] Build passes: `npm run build` in /Users/soup/flume
- [ ] Tests pass: `npm test -- --run` in /Users/soup/flume

## Key Files
- `/Users/soup/flume/app/page.tsx` — homepage source
- `/Users/soup/flume/app/globals.css` — global styles
