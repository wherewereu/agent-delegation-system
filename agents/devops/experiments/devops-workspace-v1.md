# DEVOPS Workspace Autoresearch — v1

**Date:** 2026-03-25
**Agent:** Devops (Infrastructure & Deployment)
**Author:** Einstein (subagent audit)

---

## PHASE 1: BASELINE SCORING (3 tasks × 6 questions)

### TASK A: "Set up CI/CD for flume-crm on GitHub Actions"

| # | Question | Score | Evidence |
|---|----------|-------|----------|
| 1 | Workspace loaded? | ✅ YES | AGENTS.md Session Startup loads SOUL.md + IDENTITY.md + USER.md |
| 2 | Skill followed? | ⚠️ PARTIAL | TOOLS.md lists `github` + `cloudflare-pages` skills. But AGENTS.md startup does NOT read task-specific skills. No CI/CD skill is loaded or followed. |
| 3 | Output saved correctly? | ✅ YES | Would create `.github/workflows/` — correct location |
| 4 | Delegation protocol? | ❌ NO | No reporting to Hoss mid-task. AGENTS.md has no delegation protocol for Devops. |
| 5 | In character? | ⚠️ PARTIAL | Zero-downtime obsessed — would write good CI/CD. But no rollback strategy for failed runs. |
| 6 | Memory updated? | ❌ NO | No memory/ directory exists. No logging after task. |

**Task A Score: 2.5/6**

---

### TASK B: "Debug why the cloudflared tunnel keeps disconnecting"

| # | Question | Score | Evidence |
|---|----------|-------|----------|
| 1 | Workspace loaded? | ✅ YES | Same startup sequence |
| 2 | Skill followed? | ❌ NO | `cloudflare` skill exists at `~/.openclaw/skills/cloudflare/SKILL.md` but is NEVER loaded in startup or task execution. |
| 3 | Output saved correctly? | ❌ N/A | No output would be produced (diagnostic task, no artifact path defined) |
| 4 | Delegation protocol? | ❌ NO | No Hoss escalation. SOUL.md says "escalate issues to Hoss if systems go down" but no protocol for HOW. |
| 5 | In character? | ✅ YES | Reliable, systematic — would log tunnel state, check cloudflared logs, document findings. |
| 6 | Memory updated? | ❌ NO | No memory/ dir. Lessons from tunnel debugging would be lost. |

**Task B Score: 1.5/6**

---

### TASK C: "Deploy the FastAPI backend to Railway"

| # | Question | Score | Evidence |
|---|----------|-------|----------|
| 1 | Workspace loaded? | ✅ YES | Same startup |
| 2 | Skill followed? | ❌ NO | TOOLS.md mentions `railway up` but NO skill file for Railway deployment exists. `deploy-render` is listed but Railway-specific deployment SKILL.md is not loaded. |
| 3 | Output saved correctly? | ✅ YES | Would use Railway CLI. TOOLS.md documents this correctly. |
| 4 | Delegation protocol? | ❌ NO | No Hoss status update after deploy. No next-steps reporting. |
| 5 | In character? | ⚠️ PARTIAL | Zero-downtime — Railway blue/green helps. But no rollback plan documented in workspace. |
| 6 | Memory updated? | ❌ NO | No memory/. No log of Railway deployment decisions. |

**Task C Score: 2/6**

---

## PHASE 2: TOP FAILURE PATTERN

**Pattern: SKILL NOT LOADED on task start**

The workspace's AGENTS.md Session Startup reads:
```
1. Read SOUL.md — this is who you are
2. Read USER.md — this is who you're helping
3. Read memory/YYYY-MM-DD.md (today + yesterday)
```

But it **never reads task-specific skills**. Devops is an infrastructure agent — every task requires deployment/infrastructure skills (docker, cloudflare, github, deploy-*). Yet AGENTS.md has no instruction to load a skill based on the task at hand.

**Consequences:**
- Task B (cloudflared): The `cloudflare` skill exists but is never used → suboptimal debugging
- Task C (Railway): No Railway SKILL.md exists at all → Devops would improvise
- Task A (GitHub Actions): `github` skill exists but isn't loaded → may miss best practices

**Secondary pattern: No delegation protocol**
AGENTS.md has no instruction to report task status to Hoss. SOUL.md mentions escalation but no mechanism.

**Tertiary pattern: No memory infrastructure**
`memory/` directory doesn't exist. No logging after task completion.

---

## PHASE 3: ONE SURGICAL FIX

**Fix:** Update `AGENTS.md` — replace generic Session Startup with a Devops-specific one that loads task-relevant skills.

**Current AGENTS.md Session Startup (generic, not Devops-specific):**
```
## Session Startup
Before doing anything else:
1. Read SOUL.md — this is who you are
2. Read USER.md — this is who you're helping
3. Read memory/YYYY-MM-DD.md (today + yesterday)
```

**Proposed fix — insert into AGENTS.md before "## Memory" section:**

```
## Session Startup (Devops-Specific)

Before doing anything else:

1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. Read `HEARTBEAT.md` — active tasks and infrastructure state

## Task Execution Protocol

When assigned a deployment/infrastructure task:

1. **Load relevant skill FIRST** based on task type:
   - GitHub Actions/CI → read `~/.openclaw/skills/github/SKILL.md`
   - Docker/containers → read `~/.openclaw/skills/docker/SKILL.md`
   - Cloudflare/tunnels → read `~/.openclaw/skills/cloudflare/SKILL.md`
   - Railway/Render → read TOOLS.md deployment section
   - Cloudflare Pages → read `~/.openclaw/skills/frontend-dev/SKILL.md`

2. **Create working dir** for task outputs:
   - CI/CD → `.github/workflows/`
   - Docker → `docker/`
   - Cloudflare → `cloudflare/`
   - Docs → `docs/infra/`

3. **Report to Hoss**: After completing a task, send a brief status message with:
   - What was done
   - Where configs were saved
   - Any blockers or next steps

4. **Log it**: After task completion, write a brief entry to `memory/YYYY-MM-DD.md`:
   - Task description
   - Key decisions made
   - Config files created/modified
   - Any issues encountered
```

---

## PHASE 4: APPLY FIX

**File to modify:** `/Users/soup/.openclaw/workspace/agents/devops/AGENTS.md`

**Insert:** Task Execution Protocol section after Session Startup

**Also create:** `memory/` directory and initial `memory/2026-03-25.md`

---

## RECOMMENDED FOLLOW-UPS (not part of this fix)

1. Create `~/.openclaw/skills/railway/SKILL.md` — Railway-specific deployment guide (gap found in Task C)
2. Add `memory/` directory with initial state file
3. Add delegation logging script reference to AGENTS.md delegation section
4. Update SOUL.md escalation section with specific protocol (e.g., "if system down > 5min, message Hoss with: service, symptoms, actions taken")
