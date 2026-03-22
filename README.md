<!-- Improved compatibility of back to top link -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1>🤖 Agent Delegation System</h1>
  <p><strong>Multi-agent task routing and orchestration for OpenClaw</strong></p>
  <p>
    <a href="#what-are-openclaw-subagents">What are Subagents?</a>
    ·
    <a href="#setting-up-subagents">Set Up Subagents</a>
    ·
    <a href="#architecture">Architecture</a>
    ·
    <a href="#discord-setup">Discord Setup</a>
    ·
    <a href="#agents">Agents</a>
  </p>
</div>

---

## What are OpenClaw Subagents?

> **These are OpenClaw subagents (also called spawned agents).** They are not separate processes or independent programs — they are *sessions spawned by the main orchestrator agent* to handle specialized tasks.

In OpenClaw, a **subagent** (or *spawned agent*) is a dedicated agent session that the main orchestrator (Milo) spawns on demand to handle a specific task domain. Think of it like a manager delegating work to specialists — Milo stays in charge, but offloads research, email, coding, and other specialized work to agents who are experts in those areas.

### Key concepts

| Concept | Description |
|---------|-------------|
| **Main agent** | Your primary OpenClaw agent (e.g., Milo). All user requests come here first. |
| **Spawned agent** | A subagent session created by the main agent to handle a specific task. |
| **sessions_yield** | The OpenClaw tool the main agent uses to spawn a subagent and hand off a task. |
| **Skill** | Each agent has a `SKILL.md` that defines its role, behavior, and rules. |
| **Workspace isolation** | Each agent has its own workspace (`SOUL.md`, `memory/`, skills) — separate from the main agent. |

### How spawning works

When Milo (the orchestrator) receives a request, it:

1. **Classifies the intent** — is this research? email? a doctor visit reminder?
2. **Checks availability** — is the right agent free?
3. **Spawns a subagent** using `sessions_yield` — the subagent wakes up with its own skill file loaded and a specific task to complete.
4. **Monitors and receives results** — the subagent completes its work and results flow back to Milo.
5. **Reports to the user** — Milo delivers the final answer.

### Why use subagents?

- **Focus** — Each agent only knows its domain. No prompt pollution from irrelevant keywords.
- **Parallelism** — Multiple subagents can work simultaneously on independent tasks.
- **Specialization** — Archie is great at research. Heph is great at code. You don't ask the wrong agent.
- **Debugging** — Tasks are isolated. If something breaks, you know exactly which agent to inspect.

---

## Setting Up OpenClaw Subagents

This section walks you through setting up your own multi-agent team using **only OpenClaw** — no custom infrastructure required.

### Prerequisites

| Dependency | Version | Purpose |
|-----------|---------|---------|
| [OpenClaw](https://openclaw.ai) | Latest | Agent orchestration framework |
| Node.js | 18+ | Runtime |
| Git | 2.30+ | Version control |
| A Discord server | — | Command center (optional but recommended) |

### Step 1 — Install OpenClaw

```bash
npm install -g openclaw@latest
openclaw setup
```

### Step 2 — Understand how subagents are spawned

OpenClaw subagents are **spawned sessions** — they are not separate processes you run independently. The main agent uses the `sessions_yield` tool to spin up a subagent session for a specific task.

The spawn is defined by:
- **A skill file** (`SKILL.md`) — the agent's brain, defining its role, rules, and behavior
- **A task prompt** — what the subagent should do in this specific session
- **A workspace** — the subagent's own file system space for memory, notes, and working files

Each subagent is a **lightweight session** that loads its skill, does its work, and returns results. You don't run them as persistent background services — the main agent spawns them as needed.

### Step 3 — Create your agent skill files

Each specialist agent needs a `SKILL.md` file that defines who it is and what it does. Create a directory for each agent under your workspace:

```bash
mkdir -p ~/.openclaw/workspace/skills/archie
mkdir -p ~/.openclaw/workspace/skills/merc
mkdir -p ~/.openclaw/workspace/skills/eris
# ... etc
```

#### Example: Archie's SKILL.md

```markdown
---
name: archie
description: Research specialist agent. Handles web searches, fact-finding, and information retrieval.
---

# Archimedes (Archie)

## Role
Research and information retrieval. You are spawned by the main orchestrator agent to handle research tasks.

## What You Do
- Search the web for relevant information
- Verify facts across multiple sources
- Deliver structured findings to the orchestrator

## Output Format
Return a structured brief:
- Topic: [what you researched]
- Summary: [2-3 sentence summary]
- Key Findings: [bullet points]
- Sources: [links]

## Rules
- Always cite your sources
- Lead with the most important finding
- Never extrapolate beyond what sources say
```

### Step 4 — Spawn subagents using sessions_yield

From within the main agent (Milo), the orchestrator spawns a subagent like this:

```
The main agent calls sessions_yield with:
- skill: "archie"              # the skill name
- prompt: "Research the latest AI news for Justine's Amazon SME role"
- label: "research-ai-news"    # session label for tracking
```

The `sessions_yield` tool:
1. Creates a new session for the subagent
2. Loads the agent's `SKILL.md` (its brain)
3. Injects the task prompt
4. Runs the subagent to completion
5. Returns results to the main agent

### Step 5 — Create agent workspaces (optional but recommended)

For more persistent agents with their own memory and long-term context, create dedicated workspaces:

```bash
# Create a workspace for Archie
openclaw agents add archie --workspace ~/.openclaw/workspace/archie

# Create a workspace for Merc
openclaw agents add merc --workspace ~/.openclaw/workspace/merc
```

This gives each agent:
- Its own `SOUL.md`, `AGENTS.md`, `USER.md`
- Its own session store
- Its own memory files

### Step 6 — Connect Discord for team visibility (recommended)

Each agent posts its activity to Discord channels so the whole team is visible:

```bash
# Install the Discord poster script
chmod +x ~/.openclaw/discord-post.py

# Test it
python3 ~/.openclaw/discord-post.py Archie "🧪 Test" --channel <your-channel-id>
```

See the [Discord Setup](#discord-setup) section for full details.

### Directory Structure

```
~/.openclaw/
├── workspace/               # Main agent (Milo) workspace
│   ├── SOUL.md
│   ├── AGENTS.md
│   ├── skills/
│   └── memory/
├── agents/                  # Isolated agent state directories
│   ├── main/
│   ├── archie/
│   ├── merc/
│   └── ...                  # one per agent
└── skills/                  # Shared skills
    └── archimedes/
        └── SKILL.md
```

### Quick Reference: Adding a New Agent

1. **Create the skill file** at `~/.openclaw/skills/<agent-name>/SKILL.md`
2. **Create the workspace** (optional):
   ```bash
   openclaw agents add <agent-name> --workspace ~/.openclaw/workspace/<agent-name>
   ```
3. **Add routing keywords** to the orchestrator's classification logic
4. **Create Discord channels** (optional): output, logs, memory
5. **Done** — the orchestrator can now spawn this agent

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Architecture

### System Diagram

```
User Request
    │
    ▼
┌──────────────────────────────────────┐
│           MILO (Orchestrator)         │
│  ┌────────────────────────────────┐  │
│  │     Intent Classifier           │  │
│  │  (keyword matching + confidence)│  │
│  └────────────────────────────────┘  │
└──────────────┬───────────────────────┘
               │
    ┌──────────┼──────────┬───────────┬──────────┐
    ▼          ▼          ▼           ▼          ▼
┌────────┐ ┌───────┐ ┌───────┐ ┌────────┐ ┌───────┐
│ Archie │ │ Merc  │ │ Eris  │ │  Atro  │ │ Herc  │
│Research│ │  Comms│ │Procure│ │Calendar│ │ Health│
└────────┘ └───────┘ └───────┘ └────────┘ └───────┘

    ┌──────────┐                    ┌────────┐
    │   Heph   │ ────────────────►  │  Theo  │
    │   Code   │  (auto-review)     │ Review │
    └──────────┘                    └────────┘

┌──────────────────────────────────────────────────┐
│           DISCORD COMMAND CENTER                  │
│  (delegation logs, completion reports, errors)   │
└──────────────────────────────────────────────────┘
```

### Intent Classification

Tasks are classified using a **keyword-matching algorithm** with confidence scoring:

1. **Preprocessing** — normalize input (lowercase, strip punctuation, tokenize)
2. **Keyword matching** — score each agent category by matching keywords
3. **Confidence threshold** — decide whether to auto-delegate or escalate

| Confidence | Action |
|------------|--------|
| ≥ 0.7 | Auto-delegate immediately |
| 0.4 – 0.69 | Delegate with monitoring |
| < 0.4 | Escalate to Milo for manual routing |

### Routing Rules

| Agent | Specialization | Max Concurrent | Fallback |
|-------|----------------|:--------------:|----------|
| Archie | Research / information retrieval | 3 | Milo |
| Merc | Email, messaging, social | 5 | Milo |
| Eris | Shopping, ordering, procurement | 2 | Milo |
| Atro | Calendar, scheduling, reminders | 5 | Milo |
| Herc | Health, nutrition, wellness | 3 | Milo |
| Heph | Code, scripting, automation | 2 | Theo |
| Theo | Code review, QA, verification | 3 | Milo |

### Communication Protocol

Agents communicate via a **mesh relay** (`http://MESH_RELAY_IP:8500/messages/send`) using a standardized JSON envelope:

```json
{
  "message_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "from_agent": "milo",
  "to_agent": "archie",
  "task_type": "research",
  "payload": {
    "user_request": "string",
    "context": {},
    "priority": "normal",
    "callback_channel": "telegram"
  },
  "status": "pending"
}
```

**Delivery guarantees:** At-least-once. Retries: 3 attempts with exponential backoff. Timeout: 30 seconds.

### Error Handling

| Error | Response |
|-------|----------|
| Agent timeout | Retry same agent up to 3×, then fallback or escalate |
| Agent unavailable | Queue task, notify when agent is free |
| Classification failure (< 0.4) | Milo handles manually |
| Communication failure | Retry 3×, then dead-letter queue |
| Task rejected by agent | Re-route or Milo handles |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Agents

### Milo — Orchestrator (Main Agent)

The central orchestrator. All user requests flow through Milo first.

- Intent classification and routing
- Spawning subagents via `sessions_yield`
- Task queue management
- Escalation handling
- Command center reporting

### Archie — Research Agent (Spawned Subagent)

Handles information retrieval and fact-finding tasks.

**Keywords:** `research`, `find`, `look up`, `search`, `what is`, `who is`, `information`

**Tools:** Web search, web fetch, fact-checking

### Merc — Communications Agent (Spawned Subagent)

Handles all outbound communication.

**Keywords:** `email`, `inbox`, `unsubscribe`, `gmail`, `message`, `send`, `post`, `linkedin`

**Tools:** Gmail, iMessage, Discord, LinkedIn

### Eris — Procurement Agent (Spawned Subagent)

Handles ordering and shopping tasks.

**Keywords:** `order`, `buy`, `instacart`, `amazon`, `grocery`, `purchase`, `shop`

**Tools:** Instacart, Amazon

### Atro — Calendar Agent (Spawned Subagent)

Manages scheduling and reminders.

**Keywords:** `calendar`, `schedule`, `remind`, `event`, `appointment`, `invite`

**Tools:** Apple Reminders, Google Calendar, Things 3

### Herc — Health Agent (Spawned Subagent)

Tracks wellness and nutrition.

**Keywords:** `water`, `walking`, `diet`, `calories`, `health`, `sleep`, `weight`, `nutrition`

**Tools:** Diet tracker, health-tracker, walking reminders

### Heph — Code Agent (Spawned Subagent)

Handles programming and automation tasks.

**Keywords:** `code`, `build`, `fix`, `script`, `create`, `program`, `function`, `automation`

**Tools:** File read/write, shell scripting, code generation

> All Heph output is automatically routed to Theo for review before delivery.

### Theo — Review Agent (Spawned Subagent)

Quality assurance and code review.

**Keywords:** `review`, `check`, `verify`, `audit`, `test`, `validate`, `approve`

**Role:** Reviews all Heph output, returns `APPROVED` or `REVISE` with feedback

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started

### Prerequisites

| Dependency | Version | Purpose |
|-----------|---------|---------|
| OpenClaw | Latest | Agent orchestration framework |
| Node.js | 18+ | Runtime |
| Git | 2.30+ | Version control |

**Recommended:** macOS 14+ or Ubuntu 22.04+, 8 GB RAM, low-latency network.

### Installation

1. **Install OpenClaw:**
   ```bash
   npm install -g openclaw
   openclaw setup
   ```

2. **Install the delegation skill:**
   ```bash
   openclaw skill install ~/Projects/agent-delegation-system/skill/
   ```

3. **Set environment variables:**
   ```bash
   export MINIMAX_API_KEY="your-api-key"
   export TELEGRAM_BOT_TOKEN="your-telegram-token"
   export DISCORD_WEBHOOK_URL="your-webhook-url"
   ```

4. **Configure mesh relay** (for inter-agent communication):
   ```
   http://MESH_RELAY_IP:8500/messages/send
   ```

5. **Create agent directories** with `SOUL.md` and `memory/` for each agent.

### Directory Structure

```
~/.openclaw/
├── workspace/
│   ├── agents/
│   │   ├── milo/           # Orchestrator
│   │   ├── archie/         # Research
│   │   ├── merc/           # Communications
│   │   ├── eris/           # Procurement
│   │   ├── atro/           # Calendar
│   │   ├── herc/           # Health
│   │   ├── heph/           # Code
│   │   └── theo/           # Review
│   └── skills/
└── config/
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Discord Setup

This system uses Discord as its **command center** — every agent posts delegation events, task completions, and errors to dedicated Discord channels. Before the system runs, you need a Discord server, a bot application, and all agents configured with their channel IDs.

---

### Server

| Property | Value |
|---|---|
| **Server Name** | Milo's Enterprise |
| **Server ID** | `YOUR_SERVER_ID` |
| **Bot App ID** | `1483871309677985953` |

---

### Prerequisites

- A Discord server where you have **Administrator** permissions
- Developer Mode enabled (`User Settings` → `Advanced` → `Developer Mode`) to copy channel IDs
- Account at [discord.com/developers](https://discord.com/developers) to create bot applications

---

### Step 1 — Create a Discord Application for Each Agent

Each spawned agent needs its own Discord application and bot token. Create one application per agent: **Milo, Archie, Merc, Eris, Atro, Herc, Heph, Theo.**

1. Go to [discord.com/developers](https://discord.com/developers) → **Applications** → **New Application**
2. Give it a name (e.g., `Archie`) → click **Create**
3. On the left sidebar, click **Bot** → copy the **Token** (click **Reset Token** if none exists — Discord only shows it once)
4. Click **OAuth2** → **URL Generator**
5. Under **Scopes**, check: `bot`
6. Under **Bot Permissions**, check: `Send Messages`, `Read Message History`, `Embed Links`
7. Copy the generated **OAuth2 URL** and open it in your browser to add the bot to your server

**Repeat for all 8 spawned agents.** Store each token securely — you'll need them all for the config file.

---

### Step 2 — Set Up Channels

Each spawned agent has three dedicated channels:

| Agent | Output Channel ID | Logs Channel ID | Memory Channel ID |
|---|---|---|---|
| **Command Center** (Milo) | `YOUR_COMMAND_CENTER_CHANNEL_ID` | — | — |
| **Archimedes** (archie) | `YOUR_ARCHIE_OUTPUT_CHANNEL_ID` | `YOUR_ARCHIE_LOGS_CHANNEL_ID` | `YOUR_ARCHIE_MEMORY_CHANNEL_ID` |
| **Mercury** (merc) | `YOUR_MERC_OUTPUT_CHANNEL_ID` | `YOUR_MERC_LOGS_CHANNEL_ID` | `YOUR_MERC_MEMORY_CHANNEL_ID` |
| **Eris** | `YOUR_ERIS_OUTPUT_CHANNEL_ID` | `YOUR_ERIS_LOGS_CHANNEL_ID` | `YOUR_ERIS_MEMORY_CHANNEL_ID` |
| **Atropos** (atro) | `YOUR_ATRO_OUTPUT_CHANNEL_ID` | `YOUR_ATRO_LOGS_CHANNEL_ID` | `YOUR_ATRO_MEMORY_CHANNEL_ID` |
| **Heracles** (herc) | `YOUR_HERC_OUTPUT_CHANNEL_ID` | `YOUR_HERC_LOGS_CHANNEL_ID` | `YOUR_HERC_MEMORY_CHANNEL_ID` |
| **Hephaestus** (heph) | `1483944411795816641` | — | — |
| **Themis** (theo) | `1483944415985930300` | — | — |

> Enable Developer Mode in Discord to right-click channels and **Copy Channel ID**.

**Channel purpose:**
- **Output** — the spawned agent's primary results and responses
- **Logs** — detailed execution logs for debugging
- **Memory** — stores completed task context to prevent duplicate work

---

### Step 3 — Configure the Token and Channel File

Create `~/.openclaw/agent-bot-tokens.json`:

```json
{
  "guild_id": "YOUR_SERVER_ID",
  "round_table_channel": "1483982757523750942",
  "bots": {
    "Milo":    "YOUR_MILO_BOT_TOKEN",
    "Archie":  "YOUR_ARCHIE_BOT_TOKEN",
    "Merc":    "YOUR_MERC_BOT_TOKEN",
    "Eris":    "YOUR_ERIS_BOT_TOKEN",
    "Atro":    "YOUR_ATRO_BOT_TOKEN",
    "Herc":    "YOUR_HERC_BOT_TOKEN",
    "Heph":    "YOUR_HEPH_BOT_TOKEN",
    "Theo":    "YOUR_THEO_BOT_TOKEN"
  },
  "channels": {
    "command-center":        "YOUR_COMMAND_CENTER_CHANNEL_ID",
    "archie-output":          "YOUR_ARCHIE_OUTPUT_CHANNEL_ID",
    "archie-logs":           "YOUR_ARCHIE_LOGS_CHANNEL_ID",
    "archie-memory":         "YOUR_ARCHIE_MEMORY_CHANNEL_ID",
    "merc-output":           "YOUR_MERC_OUTPUT_CHANNEL_ID",
    "merc-logs":             "YOUR_MERC_LOGS_CHANNEL_ID",
    "merc-memory":           "YOUR_MERC_MEMORY_CHANNEL_ID",
    "eris-output":           "YOUR_ERIS_OUTPUT_CHANNEL_ID",
    "eris-logs":             "YOUR_ERIS_LOGS_CHANNEL_ID",
    "eris-memory":          "YOUR_ERIS_MEMORY_CHANNEL_ID",
    "atro-output":           "YOUR_ATRO_OUTPUT_CHANNEL_ID",
    "atro-logs":             "YOUR_ATRO_LOGS_CHANNEL_ID",
    "atro-memory":          "YOUR_ATRO_MEMORY_CHANNEL_ID",
    "herc-output":           "YOUR_HERC_OUTPUT_CHANNEL_ID",
    "herc-logs":             "YOUR_HERC_LOGS_CHANNEL_ID",
    "herc-memory":          "YOUR_HERC_MEMORY_CHANNEL_ID",
    "heph-output":           "1483944411795816641",
    "theo-output":           "1483944415985930300",
    "round-table":           "1483982757523750942",
    "break-room":            "1485043346132045824"
  }
}
```

---

### Step 4 — Install the Discord Poster Script

The `discord-post.py` script posts as any agent to any channel, reading tokens from the config above.

**Location:** `~/.openclaw/discord-post.py`

```python
#!/usr/bin/env python3
"""
Agent Discord poster — posts as individual agent bots.
Usage:
  python3 ~/.openclaw/discord-post.py <agent_name> <message>
  python3 ~/.openclaw/discord-post.py <agent_name> <message> --channel <channel_id>
  python3 ~/.openclaw/discord-post.py <agent_name> <message> --reply-to <message_id>
  python3 ~/.openclaw/discord-post.py <agent_name> <message> --react-to <message_id>
"""
import sys, json, http.client

config = json.load(open('/Users/justinedelano/.openclaw/agent-bot-tokens.json'))

agent = sys.argv[1]
message = sys.argv[2]
reply_to = None
channel_id = config['round_table_channel']  # defaults to round-table

if '--reply-to' in sys.argv:
    reply_to = sys.argv[sys.argv.index('--reply-to') + 1]

if '--channel' in sys.argv:
    channel_id = sys.argv[sys.argv.index('--channel') + 1]

token = config['bots'].get(agent)
if not token:
    print(f"Unknown agent: {agent}")
    sys.exit(1)

payload = {"content": message}
if reply_to:
    payload["message_reference"] = {"message_id": reply_to}

conn = http.client.HTTPSConnection("discord.com")
conn.request(
    "POST",
    f"/api/v10/channels/{channel_id}/messages",
    body=json.dumps(payload),
    headers={
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (https://openclaw.ai, 1.0)"
    }
)
resp = conn.getresponse()
data = json.loads(resp.read())
if resp.status == 200:
    print(f"Posted as {agent} to {channel_id}, message_id: {data['id']}")
else:
    print(f"Failed: {resp.status} {data}")

if '--react-to' in sys.argv:
    msg_id = sys.argv[sys.argv.index('--react-to') + 1]
    encoded_emoji = "%E2%9C%85"  # ✅
    conn.request(
        "PUT",
        f"/api/v10/channels/{channel_id}/messages/{msg_id}/reactions/{encoded_emoji}/@me",
        body=None,
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "DiscordBot (https://openclaw.ai, 1.0)"
        }
    )
    if conn.getresponse().status == 204:
        print(f"Reacted with ✅ to message {msg_id}")
```

**Make it executable:**
```bash
chmod +x ~/.openclaw/discord-post.py
```

**Verify it works:**
```bash
python3 ~/.openclaw/discord-post.py Milo "🧪 Test" --channel YOUR_COMMAND_CENTER_CHANNEL_ID
```

If you get `403 Forbidden` — the bot lacks **Send Messages** permission in that channel. Go to the channel → **Edit Channel** → **Permissions** → grant the bot role `Send Messages`.

---

### Workflow

The delegation system runs on a strict command-and-report loop:

```
1. User posts in #command-center
        │
        ▼
2. Milo analyzes intent → routes to specialist spawned agent
        │
        ▼
3. Spawned agent posts to its OUTPUT channel (what it did)
        │
        ▼
4. Spawned agent updates MEMORY channel (prevents duplicate work)
        │
        ▼
5. Milo posts completion summary back to #command-center
```

---

### How Each Agent Posts

#### Milo — `#🎯-command-center` (`YOUR_COMMAND_CENTER_CHANNEL_ID`)

```bash
# Before delegating
python3 ~/.openclaw/discord-post.py Milo "🎯 DELEGATING
Task: [user request]
To: [agent name]
Instructions: [what you told them]" --channel YOUR_COMMAND_CENTER_CHANNEL_ID

# After task completes
python3 ~/.openclaw/discord-post.py Milo "🎯 COMPLETE
Task: [original task]
Agent: [who did it]
Result: [outcome]" --channel YOUR_COMMAND_CENTER_CHANNEL_ID
```

#### Spawned Sub-agents — each has 3 channels

| Post | Where | When |
|---|---|---|
| **START** | Output channel | Before starting work |
| **Progress / Logs** | Logs channel | During execution |
| **Memory update** | Memory channel | After completion (prevents duplicate work) |
| **COMPLETE** | Output channel | Final result |

```bash
# Example: Archie (spawned subagent) handling a research task
python3 ~/.openclaw/discord-post.py Archie "🔍 START
Researching: [task]" --channel YOUR_ARCHIE_OUTPUT_CHANNEL_ID

python3 ~/.openclaw/discord-post.py Archie "📋 LOG
Steps taken: [what Archie did]" --channel YOUR_ARCHIE_LOGS_CHANNEL_ID

python3 ~/.openclaw/discord-post.py Archie "🧠 MEMORY
Task: [task summary] | Result: [outcome]" --channel YOUR_ARCHIE_MEMORY_CHANNEL_ID

python3 ~/.openclaw/discord-post.py Archie "✅ COMPLETE
Task: [original request]
Result: [findings]" --channel YOUR_ARCHIE_OUTPUT_CHANNEL_ID
```

> **Hard rule:** If it's not in Discord, it didn't happen. Every delegation event must be logged.

---

### Inter-Agent Communication

| Layer | Tool | What it handles |
|---|---|---|
| **Human-visible coordination** | Discord channels | Activity logs, completion reports, error visibility |
| **Internal task routing** | Mesh relay (`http://MESH_RELAY_IP:8500/messages/send`) | Task delegation from Milo → specialist spawned agents |

**Mesh relay message envelope:**
```json
{
  "message_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "from_agent": "milo",
  "to_agent": "archie",
  "task_type": "research",
  "payload": {
    "user_request": "string",
    "context": {},
    "priority": "normal",
    "callback_channel": "discord"
  },
  "status": "pending"
}
```

Delivery: at-least-once, 3 retries with exponential backoff, 30s timeout.

---

### Configuration Reference

All Discord config lives in `~/.openclaw/agent-bot-tokens.json`:

| Key | Description |
|---|---|
| `guild_id` | Server ID: `YOUR_SERVER_ID` |
| `bots.Milo` | Orchestrator bot token |
| `bots.Archie` | Research spawned agent bot token |
| `bots.Merc` | Communications spawned agent bot token |
| `bots.Eris` | Procurement spawned agent bot token |
| `bots.Atro` | Calendar spawned agent bot token |
| `bots.Herc` | Wellness spawned agent bot token |
| `bots.Heph` | Code spawned agent bot token |
| `bots.Theo` | Review spawned agent bot token |
| `channels.command-center` | Milo's delegation log: `YOUR_COMMAND_CENTER_CHANNEL_ID` |
| `channels.archie-output` | Archie's output: `YOUR_ARCHIE_OUTPUT_CHANNEL_ID` |
| `channels.archie-logs` | Archie's logs: `YOUR_ARCHIE_LOGS_CHANNEL_ID` |
| `channels.archie-memory` | Archie's memory: `YOUR_ARCHIE_MEMORY_CHANNEL_ID` |
| `channels.merc-output` | Merc's output: `YOUR_MERC_OUTPUT_CHANNEL_ID` |
| `channels.merc-logs` | Merc's logs: `YOUR_MERC_LOGS_CHANNEL_ID` |
| `channels.merc-memory` | Merc's memory: `YOUR_MERC_MEMORY_CHANNEL_ID` |
| `channels.eris-output` | Eris's output: `YOUR_ERIS_OUTPUT_CHANNEL_ID` |
| `channels.eris-logs` | Eris's logs: `YOUR_ERIS_LOGS_CHANNEL_ID` |
| `channels.eris-memory` | Eris's memory: `YOUR_ERIS_MEMORY_CHANNEL_ID` |
| `channels.atro-output` | Atro's output: `YOUR_ATRO_OUTPUT_CHANNEL_ID` |
| `channels.atro-logs` | Atro's logs: `YOUR_ATRO_LOGS_CHANNEL_ID` |
| `channels.atro-memory` | Atro's memory: `YOUR_ATRO_MEMORY_CHANNEL_ID` |
| `channels.herc-output` | Herc's output: `YOUR_HERC_OUTPUT_CHANNEL_ID` |
| `channels.herc-logs` | Herc's logs: `YOUR_HERC_LOGS_CHANNEL_ID` |
| `channels.herc-memory` | Herc's memory: `YOUR_HERC_MEMORY_CHANNEL_ID` |
| `channels.heph-output` | Heph's output: `1483944411795816641` |
| `channels.theo-output` | Theo's output: `1483944415985930300` |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Usage

### Delegation Flow (CLI)

#### Classify an intent

```bash
./scripts/classify-intent.sh "is it going to rain today?"
# Output: ARCHIE (confidence: 0.85)
```

#### Check agent availability

```bash
./scripts/check-agent.sh archie
# Output: AVAILABLE (current load: 1/3)
```

#### Delegate a task

```bash
./scripts/delegate.sh archie "what is the capital of France?" normal
# Output: Delegation ID: uuid | Status: assigned
```

### Delegation Flow (OpenClaw)

When Milo (the main orchestrator) receives a user request:

```
User: "remind me to call mom at 5pm"

1. Milo analyzes → "remind me to call mom at 5pm"
2. Intent classify → Calendar (confidence: 0.92)
3. Check availability → Atro available (2/5 tasks)
4. Spawn subagent → Atro receives task via sessions_yield
5. Execute → Atro creates reminder at 5pm
6. Report → "Done! Reminder set for 5pm"
```

### Example Delegations

| User Request | Spawned Agent | Result |
|---|---|---|
| "is it going to rain today?" | Archie | "No rain, 72°F sunny" |
| "remind me to call mom at 5pm" | Atro | Reminder created |
| "order more coffee" | Eris | Added to Instacart cart |
| "write a script to backup my files" | Heph → Theo | Script created, reviewed, approved |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Known Limitations

1. **Single orchestrator** — Milo must be online for delegation to work
2. **Sequential Heph → Theo** — code review adds latency (no parallelization)
3. **API rate limits** — MiniMax rate limits apply per agent
4. **Context window** — large conversations may lose delegation context

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not responding | Check memory files, restart agent |
| Delegation failing | Verify mesh relay connection |
| Classification errors | Adjust keyword weights in `SPEC.md` |
| API errors | Check API key validity and rate limits |

See `REQUIREMENTS.md` and `SPEC.md` for full details.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## License

Distributed under the Unlicense. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/wherewereu/agent-delegation-system.svg?style=for-the-badge
[contributors-url]: https://github.com/wherewereu/agent-delegation-system/graphs/contributors
[stars-shield]: https://img.shields.io/github/stars/wherewereu/agent-delegation-system.svg?style=for-the-badge
[stars-url]: https://github.com/wherewereu/agent-delegation-system/stargazers
[issues-shield]: https://img.shields.io/github/issues/wherewereu/agent-delegation-system.svg?style=for-the-badge
[issues-url]: https://github.com/wherewereu/agent-delegation-system/issues
[license-shield]: https://img.shields.io/github/license/wherewereu/agent-delegation-system.svg?style=for-the-badge
[license-url]: https://github.com/wherewereu/agent-delegation-system/blob/master/LICENSE
