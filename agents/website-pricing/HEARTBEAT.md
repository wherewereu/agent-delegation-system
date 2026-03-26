# HEARTBEAT.md — website-pricing

## My Mission
Own /pricing. Keep it accurate and in sync with /agent-hosting.

## Weekly Checks
1. Verify https://flumeusa.com/pricing returns 200
2. Confirm all 3 pricing tiers match /agent-hosting page exactly
3. Check all feature lists match (Free: 7 features, Lite: 8, Pro: 8)
4. Verify "Also from Flume" section shows clawplex + client-portal correctly
5. All CTAs link to working signup URLs
6. FAQ answers are current
7. Mobile layout at 375px

## CRITICAL: Sync with /agent-hosting
If you update pricing on /pricing, you MUST also update /agent-hosting page's pricing section.
They must ALWAYS match exactly.

## Pre-deploy Checklist
- [ ] 3 tiers with correct prices ($0, $19, $39)
- [ ] Feature lists match exactly what's on /agent-hosting
- [ ] Badge on correct tier ("MOST POPULAR" on Lite)
- [ ] "Also from Flume" section shows correct products and URLs
- [ ] All signup CTAs resolve
- [ ] Mobile responsive
- [ ] Dark theme consistent
- [ ] Build passes
- [ ] Tests pass

## Key Files
- `/Users/soup/flume/app/pricing/page.tsx`
- `/Users/soup/flume/app/pricing/PricingClient.tsx`
- `/Users/soup/flume/app/agent-hosting/page.tsx` (must stay in sync)
