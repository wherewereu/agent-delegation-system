# SKILLS.md — website-agent-hosting

## Skills for agent-hosting page ownership

### Must Read
- `~/.openclaw/skills/frontend-dev/SKILL.md` — frontend patterns
- `~/.openclaw/skills/fullstack-dev/SKILL.md` — for any backend integration

### Source Content
- `/Users/soup/flume/agent-hosting/CONTENT.md` — all real product content
- `/Users/soup/flume/agent-hosting/src/pages/Landing.jsx` — original landing page
- `/Users/soup/flume/agent-hosting/src/pages/Pricing.jsx` — pricing data

### Deployment
- `wrangler pages deploy out/ --project-name=flume --branch=main`
- Source: `/Users/soup/flume/app/agent-hosting/page.tsx`

### Testing
- `npm test -- --run app/agent-hosting` — specific test for this page
- 9 tests covering: hero, features, pricing, social proof, FAQ, dark theme

### Dark Theme
- Background: #0a0a0f
- Surface: #141419
- Accent: #ff6b00
- Text: white, muted: #71717a
