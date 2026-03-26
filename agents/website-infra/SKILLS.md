# SKILLS.md — website-infra

### Must Read
- `~/.openclaw/skills/cloudflare/SKILL.md` — Cloudflare Tunnels, DNS, CF Pages

### Cloudflare CLI
- `wrangler pages project list`
- `wrangler pages deployment list --project-name=<name>`
- `wrangler pages deploy <dir> --project-name=<name> --branch=main`
- `wrangler pages project create <name>`

### DNS
- Cloudflare Dashboard: https://dash.cloudflare.com
- CNAME records for subdomains
- For DNS changes, prefer dashboard over API (less risk of mistakes)

### GitHub Integration
- Settings → Builds and deployments → Connect to Git
- Requires: GitHub account with access to tylerdotai/flume repo
- Set production branch to: main
- Build command: npm run build
- Output directory: out

### Monitoring
- Check deploy history for failed deploys
- If deployment fails, check build logs in CF Pages dashboard
- Common issues: missing env vars, build command errors, output dir mismatch
