# SKILLS.md — website-pricing

### Must Read
- `~/.openclaw/skills/frontend-dev/SKILL.md`

### Deployment
- `wrangler pages deploy out/ --project-name=flume --branch=main`

### Testing
- `npm run build` and `npm test -- --run`

### IMPORTANT: Pricing Sync
If pricing changes, update BOTH:
1. `/Users/soup/flume/app/pricing/PricingClient.tsx`
2. `/Users/soup/flume/app/agent-hosting/page.tsx` (pricing section)

These must always match exactly.

### Dark Theme
- Background: #0a0a0f
- Accent: #ff6b00
