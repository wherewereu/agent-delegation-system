# HEARTBEAT.md — website-infra

## My Mission
Own the infrastructure. Keep everything deployed, DNS correct, and links resolving.

## Weekly Checks
1. `curl https://flumeusa.com` — should return 200
2. `curl https://flumeusa.com/agent-hosting` — should return 200
3. `curl https://flumeusa.com/pricing` — should return 200
4. `curl https://client-portal.flumeusa.com` — should return 200 (or proper redirect)
5. Check wrangler pages deployment status
6. Verify GitHub integration is connected (if disconnected, flag immediately)

## Critical: GitHub Integration
If GitHub integration is disconnected:
1. Flag immediately — this blocks auto-deploy
2. Provide link to fix: https://dash.cloudflare.com → Pages → flume → Settings → Builds and deployments → Connect to Git

## Broken Link Response
If any link on the site returns non-200:
1. Identify the source page (which file has the bad link)
2. Fix the href to correct URL
3. Deploy with wrangler
4. Commit and push to GitHub

## Deploy Process
```bash
cd /Users/soup/flume
npm run build
wrangler pages deploy out/ --project-name=flume --branch=main
```

## DNS / Subdomain Issues
For new subdomains:
1. Create CF Pages project: `wrangler pages project create <name>`
2. Deploy app: `wrangler pages deploy dist --project-name=<name> --branch=main`
3. Add CNAME in Cloudflare DNS pointing to the pages.dev domain

## Key Commands
- `wrangler pages project list` — list all CF Pages projects
- `wrangler pages deployment list --project-name=flume` — deployment history
- `curl -s -o /dev/null -w "%{http_code}" https://flumeusa.com<path>` — check any URL
