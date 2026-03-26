# OWNER.md — website-infra

## Domain
All infrastructure for flumeusa.com and subdomains

## What I Own
- Cloudflare Pages project "flume" — deployment pipeline
- DNS for flumeusa.com and all subdomains
- Cloudflare Pages dashboard access
- Deploy pipeline — GitHub integration (or manual wrangler)
- Subdomains: client-portal.flumeusa.com, command-center.flumeusa.com
- Broken link detection and fix
- Redirect chains

## Known Issues (2026-03-26)
1. **GitHub integration DISCONNECTED** — CF Pages shows "Git Provider: No"
   - Fix: https://dash.cloudflare.com → Pages → flume → Settings → Connect to Git
2. **client-portal.flumeusa.com** — subdomain not resolving
   - Needs CF Pages project + DNS CNAME record
3. **command-center.flumeusa.com** — was local-only, never deployed

## Deployment
- Manual: `wrangler pages deploy out/ --project-name=flume --branch=main`
- Until GitHub integration is reconnected, every push needs manual deploy

## Verified URLs
- flumeusa.com ✅ (200)
- flumeusa.com/agent-hosting ✅ (200)
- flumeusa.com/pricing ✅ (200)
- client-portal.flumeusa.com ❌ (not resolving)
- command-center.flumeusa.com ❌ (not deployed)

## Cloudflare Account
Dashboard: https://dash.cloudflare.com
Account ID: 52fd7f274b96876a4085c530a53b759c (verify in dashboard)

## GitHub Repo
https://github.com/tylerdotai/flume — main branch
