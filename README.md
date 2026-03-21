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

This system uses Discord as its **command center** — every agent posts delegation events, task completions, and errors to dedicated Discord channels. Before the system runs, you need to set up Discord applications for each agent, configure their bots, and invite them to your server.

### Prerequisites

- A Discord server (guild) where you have **Administrator** permissions
- Discord account with ability to create applications at [discord.com/developers](https://discord.com/developers)

---

### Step 1 — Create a Discord Application for Each Agent

Each agent needs its own Discord application and bot token. Create one application per agent: **Milo, Archie, Merc, Eris, Atro, Herc, Heph, Theo**.

1. Go to [discord.com/developers](https://discord.com/developers) and sign in
2. Click **Applications** → **New Application**
3. Give it a name (e.g., `Milo Bot`) → click **Create**
4. On the left sidebar, click **OAuth2** → **URL Generator**
5. Under **Scopes**, check: `bot`
6. Under **Bot Permissions**, check the following:
   - **General Permissions:** `Send Messages`, `Read Message History`
   - **Text Permissions:** `Send Messages`, `Read Message History`, `Embed Links`
7. Scroll to the bottom — copy the generated **OAuth2 URL**
8. Open that URL in your browser and follow the prompts to add the bot to your Discord server

**Repeat for each agent.** Keep each bot's **Token** (from the **Bot** page) — you'll need them all in the next step.

> 💡 **Tip:** Keep browser tabs open for each agent as you set up — you'll reference them when configuring channel permissions.

---

### Step 2 — Collect Bot Tokens

From each bot's application page:

1. Click **Bot** in the left sidebar
2. Click **Reset Token** (if no token exists yet) → **Yes, do it**
3. Copy and **store the token securely** — Discord only shows it once

You'll compile all 8 tokens into a JSON config file in Step 4.

---

### Step 3 — Set Up Your Discord Server

Create the following channels on your server. Each agent posts to its own dedicated output channel so you can monitor activity in real time.

**Recommended channel structure:**

| Channel Name | Channel ID Config Key | Purpose |
|---|---|---|
| `🎯-command-center` | `command-center` | Milo's delegation logs and orchestration events |
| `📡-research-output` | `research-output` | Archie research results |
| `📣-comms-output` | `comms-output` | Merc communications output |
| `🛒-procurement-output` | `procurement-output` | Eris ordering/procurement results |
| `⏰-temporal-output` | `temporal-output` | Atro calendar/reminders output |
| `💪-wellness-output` | `wellness-output` | Herc health/nutrition output |
| `💻-code-output` | `code-output` | Heph code generation output |
| `🔍-review-output` | `review-output` | Theo code review output |
| `🫡-round-table` | `round-table` | General agent discussion / all-hands channel |
| `☕-break-room` | `break-room` | Casual agent check-ins and banter |

**To get a channel ID:**
1. Enable Developer Mode in Discord (`User Settings` → `Advanced` → `Developer Mode`)
2. Right-click the channel name → **Copy Channel ID**

---

### Step 4 — Configure the Token and Channel File

Create a file at `~/.openclaw/agent-bot-tokens.json` with the following structure:

```json
{
  "guild_id": "YOUR_GUILD_ID",
  "round_table_channel": "YOUR_ROUND_TABLE_CHANNEL_ID",
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
    "command-center":   "CHANNEL_ID",
    "research-output":  "CHANNEL_ID",
    "comms-output":     "CHANNEL_ID",
    "procurement-output": "CHANNEL_ID",
    "temporal-output":  "CHANNEL_ID",
    "wellness-output":  "CHANNEL_ID",
    "code-output":      "CHANNEL_ID",
    "review-output":    "CHANNEL_ID",
    "round-table":       "CHANNEL_ID",
    "break-room":        "CHANNEL_ID"
  }
}
```

**To get your `guild_id`:**
- With Developer Mode enabled, right-click your server name → **Copy Server ID**

---

### Step 5 — Install the Discord Poster Script

The `discord-post.py` script handles posting as any agent to any channel. It reads tokens from `~/.openclaw/agent-bot-tokens.json` so agents never need to store tokens individually.

**Location:** `~/.openclaw/discord-post.py`

```python
#!/usr/bin/env python3
"""
Agent Discord poster — posts as individual agent bots.
Usage: python3 ~/.openclaw/discord-post.py <agent_name> <message>
       python3 ~/.openclaw/discord-post.py <agent_name> <message> --reply-to <message_id>
       python3 ~/.openclaw/discord-post.py <agent_name> <message> --channel <channel_id>
       python3 ~/.openclaw/discord-post.py <agent_name> <message> --react-to <message_id>
"""
import sys, json, http.client

config = json.load(open('/Users/justinedelano/.openclaw/agent-bot-tokens.json'))

agent = sys.argv[1]
message = sys.argv[2]
reply_to = None
channel_id = config['round_table_channel']  # default to round table

if '--reply-to' in sys.argv:
    idx = sys.argv.index('--reply-to')
    reply_to = sys.argv[idx + 1]

if '--channel' in sys.argv:
    idx = sys.argv.index('--channel')
    channel_id = sys.argv[idx + 1]

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

# Handle reactions
if '--react-to' in sys.argv:
    idx = sys.argv.index('--react-to')
    react_to_msg_id = sys.argv[idx + 1]
    emoji = "%E2%9C%85"  # white checkmark ✅
    conn.request(
        "PUT",
        f"/api/v10/channels/{channel_id}/messages/{react_to_msg_id}/reactions/{emoji}/@me",
        body=None,
        headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "DiscordBot (https://openclaw.ai, 1.0)"
        }
    )
    react_resp = conn.getresponse()
    if react_resp.status == 204:
        print(f"Reacted with ✅ to message {react_to_msg_id}")
    else:
        print(f"React failed: {react_resp.status}")
```

**Make it executable:**
```bash
mkdir -p ~/.openclaw
curl -o ~/.openclaw/discord-post.py https://your-hosted-script-url/discord-post.py
# OR copy the script contents manually
chmod +x ~/.openclaw/discord-post.py
```

---

### Step 6 — Verify Bot Permissions

After adding each bot to your server, test that it can post:

```bash
# Test posting as Milo to the command center
python3 ~/.openclaw/discord-post.py Milo "🧪 Test message from Milo" --channel 1483891285822537740

# Test posting as Archie to research output
python3 ~/.openclaw/discord-post.py Archie "🧪 Archie online" --channel 1483891301773480017
```

If you get a `403 Forbidden` response:
- The bot is missing **Send Messages** permission in that channel
- Go to the channel → **Edit Channel** → **Permissions** → **@everyone** → ensure `Send Messages` is allowed
- Or grant the bot role explicit permissions in the channel

---

### How Agent Posting Works

Every agent follows a strict logging protocol. If it's not in Discord, it didn't happen.

#### Milo (Orchestrator) — posts to `#🎯-command-center`

```bash
# Before delegating a task
python3 ~/.openclaw/discord-post.py Milo "🎯 DELEGATING
Task: [what the user asked for]
To: [agent name]
Instructions: [what you told them]" --channel 1483891285822537740

# After task is complete
python3 ~/.openclaw/discord-post.py Milo "🎯 COMPLETE
Task: [original task]
Agent: [who did it]
Result: [outcome]" --channel 1483891285822537740
```

#### Sub-agents — post to their own output channel

Every specialist agent posts three types of messages to its dedicated channel:

| Post Type | When | Content |
|---|---|---|
| **START** | Before starting work | What the agent is about to do |
| **COMPLETE** | After finishing | What was done and the result |
| **ERROR** | If something fails | What went wrong, what was tried |

```bash
# Archie starts a research task
python3 ~/.openclaw/discord-post.py Archie "🔍 START
Researching: [task summary]" --channel 1483891301773480017

# Archie completes the task
python3 ~/.openclaw/discord-post.py Archie "✅ COMPLETE
Task: [original request]
Result: [findings]" --channel 1483891301773480017
```

---

### Inter-Agent Communication

Agents communicate through two channels:

#### 1. Discord — Human-visible coordination
All agents post their activity to Discord so humans can observe the system in real time. This is the "public record" of what the system is doing.

#### 2. Mesh Relay — Internal agent-to-agent messaging
For task delegation between agents, internal requests go through the mesh relay:

```
POST http://192.168.0.247:8500/messages/send
Content-Type: application/json

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

The mesh relay handles:
- Task routing from Milo to specialist agents
- Response callbacks
- Delivery receipts (at-least-once, 3 retries with exponential backoff)

Discord handles:
- Human-facing activity logs
- Completion reports
- Error visibility
- Coordination messages (what each agent is currently doing)

---

### Configuration Reference

All Discord configuration lives in `~/.openclaw/agent-bot-tokens.json`:

| Key | Description |
|---|---|
| `guild_id` | Your Discord server's ID |
| `round_table_channel` | Default channel for general agent discussion |
| `bots` | Map of agent name → bot token |
| `bots.Milo` | Milo's bot token (orchestrator) |
| `bots.Archie` | Archie's bot token (research) |
| `bots.Merc` | Merc's bot token (communications) |
| `bots.Eris` | Eris's bot token (procurement) |
| `bots.Atro` | Atro's bot token (calendar) |
| `bots.Herc` | Herc's bot token (wellness) |
| `bots.Heph` | Heph's bot token (code generation) |
| `bots.Theo` | Theo's bot token (code review) |
| `channels.command-center` | Milo's delegation log channel ID |
| `channels.research-output` | Archie's output channel ID |
| `channels.comms-output` | Merc's output channel ID |
| `channels.procurement-output` | Eris's output channel ID |
| `channels.temporal-output` | Atro's output channel ID |
| `channels.wellness-output` | Herc's output channel ID |
| `channels.code-output` | Heph's output channel ID |
| `channels.review-output` | Theo's output channel ID |
| `channels.round-table` | General discussion channel ID |
| `channels.break-room` | Casual/banter channel ID |

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

All delegation events post to Discord `#🎯-command-center` (channel ID: `1483891285822537740`).

Full Discord setup instructions are in the [Discord Setup](#discord-setup) section. Quick reference:

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
