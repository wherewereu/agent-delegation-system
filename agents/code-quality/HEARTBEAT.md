# HEARTBEAT.md — code-quality

## My Mission
Keep Flume code healthy. No errors, no duplicates, no dead code.

## Weekly Checks
1. Run `npm run build` in /Users/soup/flume — should be zero errors
2. Run `npm test -- --run` — all tests should pass
3. Check for duplicate component files across repos
4. Scan for any new TypeScript errors
5. Check for console.error or unhandled promise rejections in tests

## Common Issues to Watch For
- tsconfig including too many files (add `exclude` for sibling dirs)
- Import paths that point to wrong locations
- Hardcoded URLs that should be env vars
- Leftover references to deprecated products (flume.sh, leadforge-ai, etc.)

## Priority Fixes
1. **tsconfig spillover** — if build fails with errors from wrong dirs, fix exclude
2. **Duplicate components** — extract to shared `/Users/soup/flume/shared/` package
3. **Missing tests** — any new page must have tests before deploy

## Pre-deploy Gate
- [ ] `npm run build` passes with 0 errors
- [ ] `npm test -- --run` passes with 0 failures
- [ ] No TypeScript errors (check `npx tsc --noEmit`)
- [ ] No console.error in test output

## Key Commands
```bash
cd /Users/soup/flume && npm run build
cd /Users/soup/flume && npm test -- --run
cd /Users/soup/flume && npx tsc --noEmit
```
