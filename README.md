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
    <a href="#overview">Overview</a>
    ·
    <a href="#architecture">Architecture</a>
    ·
    <a href="#getting-started">Getting Started</a>
    ·
    <a href="#discord-setup">Discord Setup</a>
    ·
    <a href="#agents">Agents</a>
    ·
    <a href="#configuration">Configuration</a>
  </p>
</div>

---

## Overview

The **Agent Delegation System** is an OpenClaw skill that enables an orchestrator agent (Milo) to automatically analyze incoming user requests and route them to the appropriate specialist agent — without manual intervention.

**What it does:**
- Classifies user intent from natural language
- Routes tasks to the right specialist agent
- Monitors task execution and handles failures
- Reports results back to the user
- Integrates with Discord command center for team visibility

**Who it's for:**
- Anyone running a multi-agent OpenClaw setup
- Power users who want automated, intelligent task routing
- Teams that need coordinated agent workflows

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
│Research│ │  Comms│ │ Procure│ │Calendar│ │ Health│
└────────┘ └───┬───┘ └───┬───┘ └────────┘ └───┬───┘
               │          │                    │
               ▼          ▼                    ▼
          ┌────────┐ ┌───────┐           ┌────────┐
          │  Email │ │ Instacart      │ Reminders│
          └────────┘ └───────┘           └────────┘

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

Agents communicate via a **mesh relay** (`http://192.168.0.247:8500/messages/send`) using a standardized JSON envelope:

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

### Milo — Orchestrator

The central orchestrator. All user requests flow through Milo first.

- Intent classification and routing
- Task queue management
- Escalation handling
- Command center reporting

### Archie — Research Agent

Handles information retrieval and fact-finding tasks.

**Keywords:** `research`, `find`, `look up`, `search`, `what is`, `who is`, `information`

**Tools:** Web search, web fetch, fact-checking

### Merc — Communications Agent

Handles all outbound communication.

**Keywords:** `email`, `inbox`, `unsubscribe`, `gmail`, `message`, `send`, `post`, `linkedin`

**Tools:** Gmail, iMessage, Discord, LinkedIn

### Eris — Procurement Agent

Handles ordering and shopping tasks.

**Keywords:** `order`, `buy`, `instacart`, `amazon`, `grocery`, `purchase`, `shop`

**Tools:** Instacart, Amazon

### Atro — Calendar Agent

Manages scheduling and reminders.

**Keywords:** `calendar`, `schedule`, `remind`, `event`, `appointment`, `invite`

**Tools:** Apple Reminders, Google Calendar, Things 3

### Herc — Health Agent

Tracks wellness and nutrition.

**Keywords:** `water`, `walking`, `diet`, `calories`, `health`, `sleep`, `weight`, `nutrition`

**Tools:** Diet tracker, health-tracker, walking reminders

### Heph — Code Agent

Handles programming and automation tasks.

**Keywords:** `code`, `build`, `fix`, `script`, `create`, `program`, `function`, `automation`

**Tools:** File read/write, shell scripting, code generation

> All Heph output is automatically routed to Theo for review before delivery.

### Theo — Review Agent

Quality assurance and code review.

**Keywords:** `review`, `check`, `verify`, `audit`, `test`, `validate`, `approve`

**Role:** Reviews all Heph output, returns `APPROVED` or `REVISE` with feedback

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Getting Started

### Prerequisites

| Dependency | Version | Purpose |
|------------|---------|---------|
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
   http://192.168.0.247:8500/messages/send
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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Discord Setup

This system uses Discord as its **command center** — every agent posts delegation events, task completions, and errors to dedicated Discord channels. Before the system runs, you need a Discord server, a bot application, and all agents configured with their channel IDs.

---

### Server

| Property | Value |
|---|---|
| **Server Name** | Milo's Enterprise |
| **Server ID** | `1483891024974840038` |
| **Bot App ID** | `1483871309677985953` |

---

### Prerequisites

- A Discord server where you have **Administrator** permissions
- Developer Mode enabled (`User Settings` → `Advanced` → `Developer Mode`) to copy channel IDs
- Account at [discord.com/developers](https://discord.com/developers) to create bot applications

---

### Step 1 — Create a Discord Application for Each Agent

Each agent needs its own Discord application and bot token. Create one application per agent: **Milo, Archie, Merc, Eris, Atro, Herc, Heph, Theo**.

1. Go to [discord.com/developers](https://discord.com/developers) → **Applications** → **New Application**
2. Give it a name (e.g., `Milo`) → click **Create**
3. On the left sidebar, click **Bot** → copy the **Token** (click **Reset Token** if none exists — Discord only shows it once)
4. Click **OAuth2** → **URL Generator**
5. Under **Scopes**, check: `bot`
6. Under **Bot Permissions**, check: `Send Messages`, `Read Message History`, `Embed Links`
7. Copy the generated **OAuth2 URL** and open it in your browser to add the bot to your server

**Repeat for all 8 agents.** Store each token securely — you'll need them all for the config file.

---

### Step 2 — Set Up Channels

Each agent has three dedicated channels:

| Agent | Output Channel ID | Logs Channel ID | Memory Channel ID |
|---|---|---|---|
| **Command Center** (Milo) | `1483891285822537740` | — | — |
| **Archimedes** (archie) | `1483891301773480017` | `1483893552877535354` | `1483893553993093231` |
| **Mercury** (merc) | `1483891383700820132` | `1483893677301436507` | `1483893678073188417` |
| **Eris** | `1483891385458491402` | `1483893679952232530` | `1483893681193746616` |
| **Atropos** (atro) | `1483891386783629322` | `1483893682514956460` | `1483893683605475348` |
| **Heracles** (herc) | `1483891388184526919` | `1483893684595458200` | `1483893685539176651` |
| **Hephaestus** (heph) | `1483944411795816641` | — | — |
| **Themis** (theo) | `1483944415985930300` | — | — |

> Enable Developer Mode in Discord to right-click channels and **Copy Channel ID**.

**Channel purpose:**
- **Output** — the agent's primary results and responses
- **Logs** — detailed execution logs for debugging
- **Memory** — stores completed task context to prevent duplicate work

---

### Step 3 — Configure the Token and Channel File

Create `~/.openclaw/agent-bot-tokens.json`:

```json
{
  "guild_id": "1483891024974840038",
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
    "command-center":        "1483891285822537740",
    "archie-output":          "1483891301773480017",
    "archie-logs":           "1483893552877535354",
    "archie-memory":         "1483893553993093231",
    "merc-output":           "1483891383700820132",
    "merc-logs":             "1483893677301436507",
    "merc-memory":           "1483893678073188417",
    "eris-output":           "1483891385458491402",
    "eris-logs":             "1483893679952232530",
    "eris-memory":          "1483893681193746616",
    "atro-output":           "1483891386783629322",
    "atro-logs":             "1483893682514956460",
    "atro-memory":          "1483893683605475348",
    "herc-output":           "1483891388184526919",
    "herc-logs":             "1483893684595458200",
    "herc-memory":          "1483893685539176651",
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
python3 ~/.openclaw/discord-post.py Milo "🧪 Test" --channel 1483891285822537740
```

If you get `403 Forbidden` — the bot lacks **Send Messages** permission in that channel. Go to the channel → **Edit Channel** → **Permissions** → grant the bot role `Send Messages`.

---

### Workflow

The delegation system runs on a strict command-and-report loop:

```
1. User posts in #command-center
        │
        ▼
2. Milo analyzes intent → routes to specialist agent
        │
        ▼
3. Agent posts to its OUTPUT channel (what it did)
        │
        ▼
4. Agent updates MEMORY channel (prevents duplicate work)
        │
        ▼
5. Milo posts completion summary back to #command-center
```

---

### How Each Agent Posts

#### Milo — `#🎯-command-center` (`1483891285822537740`)

```bash
# Before delegating
python3 ~/.openclaw/discord-post.py Milo "🎯 DELEGATING
Task: [user request]
To: [agent name]
Instructions: [what you told them]" --channel 1483891285822537740

# After task completes
python3 ~/.openclaw/discord-post.py Milo "🎯 COMPLETE
Task: [original task]
Agent: [who did it]
Result: [outcome]" --channel 1483891285822537740
```

#### Sub-agents — each has 3 channels

| Post | Where | When |
|---|---|---|
| **START** | Output channel | Before starting work |
| **Progress / Logs** | Logs channel | During execution |
| **Memory update** | Memory channel | After completion (prevents duplicate work) |
| **COMPLETE** | Output channel | Final result |

```bash
# Example: Archie handling a research task
python3 ~/.openclaw/discord-post.py Archie "🔍 START
Researching: [task]" --channel 1483891301773480017

python3 ~/.openclaw/discord-post.py Archie "📋 LOG
Steps taken: [what Archie did]" --channel 1483893552877535354

python3 ~/.openclaw/discord-post.py Archie "🧠 MEMORY
Task: [task summary] | Result: [outcome]" --channel 1483893553993093231

python3 ~/.openclaw/discord-post.py Archie "✅ COMPLETE
Task: [original request]
Result: [findings]" --channel 1483891301773480017
```

> **Hard rule:** If it's not in Discord, it didn't happen. Every delegation event must be logged.

---

### Inter-Agent Communication

| Layer | Tool | What it handles |
|---|---|---|
| **Human-visible coordination** | Discord channels | Activity logs, completion reports, error visibility |
| **Internal task routing** | Mesh relay (`http://192.168.0.247:8500/messages/send`) | Task delegation from Milo → specialist agents |

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
| `guild_id` | Server ID: `1483891024974840038` |
| `bots.Milo` | Orchestrator bot token |
| `bots.Archie` | Research agent bot token |
| `bots.Merc` | Communications agent bot token |
| `bots.Eris` | Procurement agent bot token |
| `bots.Atro` | Calendar agent bot token |
| `bots.Herc` | Wellness agent bot token |
| `bots.Heph` | Code agent bot token |
| `bots.Theo` | Review agent bot token |
| `channels.command-center` | Milo's delegation log: `1483891285822537740` |
| `channels.archie-output` | Archie's output: `1483891301773480017` |
| `channels.archie-logs` | Archie's logs: `1483893552877535354` |
| `channels.archie-memory` | Archie's memory: `1483893553993093231` |
| `channels.merc-output` | Merc's output: `1483891383700820132` |
| `channels.merc-logs` | Merc's logs: `1483893677301436507` |
| `channels.merc-memory` | Merc's memory: `1483893678073188417` |
| `channels.eris-output` | Eris's output: `1483891385458491402` |
| `channels.eris-logs` | Eris's logs: `1483893679952232530` |
| `channels.eris-memory` | Eris's memory: `1483893681193746616` |
| `channels.atro-output` | Atro's output: `1483891386783629322` |
| `channels.atro-logs` | Atro's logs: `1483893682514956460` |
| `channels.atro-memory` | Atro's memory: `1483893683605475348` |
| `channels.herc-output` | Herc's output: `1483891388184526919` |
| `channels.herc-logs` | Herc's logs: `1483893684595458200` |
| `channels.herc-memory` | Herc's memory: `1483893685539176651` |
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

### Delegation Flow (OpenClaw Skill)

When Milo receives a user request:

```
User: "remind me to call mom at 5pm"

1. Milo analyzes → "remind me to call mom at 5pm"
2. Intent classify → Calendar (confidence: 0.92)
3. Check availability → Atro available (2/5 tasks)
4. Delegate → Atro receives task
5. Execute → Atro creates reminder at 5pm
6. Report → "Done! Reminder set for 5pm"
```

### Example Delegations

| User Request | Agent | Result |
|---|---|---|
| "is it going to rain today?" | Archie | "No rain, 72°F sunny" |
| "remind me to call mom at 5pm" | Atro | Reminder created |
| "order more coffee" | Eris | Added to Instacart cart |
| "write a script to backup my files" | Heph → Theo | Script created, reviewed, approved |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Configuration

> ⚠️ **Discord configuration** (bot tokens, channel IDs, guild settings) is documented in full in the [Discord Setup](#discord-setup) section above. This section covers general task routing and intent classification configuration.

### Priority Levels

| Level | Description |
|-------|-------------|
| `urgent` | Immediate routing, interrupts queue |
| `normal` | Standard FIFO within priority |
| `low` | Background processing, lowest priority |

### Intent Keywords

Edit `SPEC.md` or the agent keyword tables to customize classification:

| Agent | Keywords |
|-------|----------|
| Archie | research, find, look up, search, what is, who is, information |
| Merc | email, inbox, unsubscribe, gmail, message, send, post |
| Eris | order, buy, instacart, amazon, grocery, purchase, shop |
| Atro | calendar, schedule, remind, event, appointment, invite |
| Herc | water, walking, diet, calories, health, sleep, weight, nutrition |
| Heph | code, build, fix, script, create, program, function, automation |
| Theo | review, check, verify, audit, test, validate, approve |

### Command Center

All delegation events post to Discord `#🎯-command-center` (`1483891285822537740`).

Full setup instructions are in [Discord Setup](#discord-setup). Quick reference:

```bash
python3 ~/.openclaw/discord-post.py Milo "YOUR_MESSAGE" --channel 1483891285822537740
```

Post types:
- **DELEGATION** — when Milo routes a task to a specialist
- **COMPLETION REPORT** — when a task finishes
- **AUTONOMOUS DECISION** — when Milo makes a non-trivial decision

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## Skill Files

```
agent-delegation-system/
├── README.md               # This file
├── REQUIREMENTS.md         # System requirements and dependencies
├── SPEC.md                 # Technical specification (intent classification, routing, error handling)
├── TODO.md                 # Roadmap and planned features
└── skill/
    ├── SKILL.md            # Skill definition for OpenClaw
    └── scripts/
        ├── delegate.sh          # Route task to a specialist agent
        ├── classify-intent.sh    # Classify user request → recommended agent
        └── check-agent.sh        # Check if an agent is available
```

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
