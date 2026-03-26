# SKILLS.md — code-quality

### Must Read
- `~/.openclaw/skills/fullstack-dev/SKILL.md` — for error handling patterns

### Key Tools
- `npm run build` — verify no build errors
- `npm test -- --run` — full test suite
- `npx tsc --noEmit` — TypeScript check
- `grep -r "flume.sh\|leadforge\|dungeon.delver" --include="*.ts" --include="*.tsx"` — find dead refs

### Deduplication
If you find duplicate files, move the canonical version to `/Users/soup/flume/shared/` and update imports.

### tsconfig Fix
If tsconfig is including wrong dirs, add to `exclude` array:
```json
"exclude": ["node_modules", "../sibling-dir", "../../other-project"]
```

### Test Coverage
Run with coverage: `npm test -- --run --coverage`
Minimum: 80% statement coverage on pages shipping to production.

### Dark Theme
When editing components: bg #0a0a0f, surface #141419, accent #ff6b00
