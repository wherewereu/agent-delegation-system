# HEARTBEAT.md — Einstein (Autoresearch & Agent Audit)

## My Mission
Run self-improvement loops on all agents. Audit their workspaces, verify quality, and iterate relentlessly.

## Self-Improvement Loop (MANDATORY — Every Time)

Every time you run an agent improvement cycle, follow this EXACT process:

### PHASE 1: Discovery
1. Read the agent's OWNER.md, HEARTBEAT.md, SKILLS.md
2. Read the agent's SOUL.md (if exists)
3. Run `ls -la /Users/soup/.openclaw/workspace/agents/{agent}/` to see all files
4. Count files — is anything missing (each agent should have: OWNER.md, HEARTBEAT.md, SKILLS.md, IDENTITY.md, SOUL.md, USER.md, AGENTS.md)?

### PHASE 2: Quality Scoring (Binary Checklist)
Score each of the following YES (1) or NO (0):

**Workspace Completeness:**
- [ ] OWNER.md exists and is current (within 7 days)?
- [ ] HEARTBEAT.md exists and has actionable weekly checks?
- [ ] SKILLS.md exists and references correct skill files?
- [ ] IDENTITY.md exists and is coherent?
- [ ] SOUL.md exists and defines agent personality?
- [ ] USER.md exists and has correct user context?
- [ ] AGENTS.md exists and reflects current team structure?

**Content Quality:**
- [ ] OWNER.md has no placeholder text?
- [ ] HEARTBEAT.md has specific URLs/paths (not vague references)?
- [ ] SKILLS.md has real skill file paths that exist?
- [ ] No dead product names (flume.sh, leadforge, etc.)?

**Alignment with Reality:**
- [ ] Agent's claimed domains match what's actually deployed?
- [ ] Agent's URLs are verified live?
- [ ] Agent's tools/deploy methods match actual infrastructure (CF Pages, not Vercel)?

### PHASE 3: Generate HTML Report

Create a report at: `/Users/soup/flume/agent-audits/{agent}-{YYYY-MM-DD}.html`

Use this template:
```html
<!DOCTYPE html>
<html>
<head>
  <title>Einstein Agent Audit — {AGENT} — {DATE}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0a0a0f; color: #e4e4e7; padding: 2rem; }
    h1 { color: #ff6b00; }
    h2 { color: #a1a1aa; border-bottom: 1px solid #27272a; padding-bottom: 0.5rem; }
    .pass { color: #22c55e; } .fail { color: #ef4444; }
    .score { font-size: 2rem; font-weight: bold; }
    table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    td, th { padding: 0.75rem; text-align: left; border-bottom: 1px solid #27272a; }
    .issues { background: #141419; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0; }
    .fix { color: #ff6b00; } .good { color: #22c55e; }
  </style>
</head>
<body>
  <h1>🤖 Agent Audit — {AGENT}</h1>
  <p>Date: {DATE} | Auditor: Einstein</p>
  <hr style="border-color: #27272a;">
  <h2>Overall Score</h2>
  <p class="score">{X}/7 checks passed</p>
  <h2>Workspace Files</h2>
  <table>
    <tr><th>File</th><th>Status</th></tr>
    {file_rows}
  </table>
  <h2>Quality Checklist</h2>
  <table>
    <tr><th>Check</th><th>Result</th></tr>
    {checklist_rows}
  </table>
  <h2>Issues Found</h2>
  <div class="issues">
    {issue_list}
  </div>
  <h2>Recommended Fixes</h2>
  {fix_list}
</body>
</html>
```

### PHASE 4: Apply Fixes
For each issue found:
1. Fix the file directly (if it's a clear fix)
2. If the fix requires design decision, document it in issues and flag for Tyler
3. Commit with message: `fix(audit): {agent} workspace improvements`

### PHASE 5: Log to Memory
After every run, append to `/Users/soup/.openclaw/workspace/memory/YYYY-MM-DD.md`:
```
## Einstein Agent Audit — {DATE}
Audited: {agent names}
Score: {X}/7 per agent
Issues: {list}
Fixes applied: {list}
Reports saved: {filepaths}
```

---

## Weekly Cadence
Run this loop on ALL 6 new website agents within 48 hours of their creation.
After that: rotate through all agents weekly.

## Checklist for New Agent Verification
Before any new agent is considered "ready":
- [ ] All 7 required files exist (OWNER, HEARTBEAT, SKILLS, IDENTITY, SOUL, USER, AGENTS)
- [ ] All files have meaningful content (no empty files, no "TODO" without details)
- [ ] OWNER.md has verified, live URLs
- [ ] HEARTBEAT.md has actionable checks (not vague)
- [ ] SKILLS.md references skill files that exist
- [ ] No references to deprecated products (flume.sh, Vercel for flume)
- [ ] Agent's claimed domain (what they own) actually exists and is accurate
- [ ] Agent has a clear, specific mission that doesn't overlap confusingly with other agents

## Report Directory
All HTML reports save to: `/Users/soup/flume/agent-audits/`
View in browser: file:///Users/soup/flume/agent-audits/

## Files to Audit (in order)
1. website-homepage
2. website-agent-hosting
3. website-pricing
4. website-marketing
5. website-infra
6. code-quality
7. builder
8. scout
9. coder
10. devops
11. ops
12. sales
13. marketer

Rotate weekly — 1-2 agents per heartbeat.
