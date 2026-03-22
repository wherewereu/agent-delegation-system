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
│ Archie │ │ Merc  │ │ Eris  │ │  Atro  │ │  Herc │
│Research│ │  Comms│ │Procure│ │Calendar│ │Health │
└────────┘ └───┬───┘ └───┬───┘ └────────┘ └───┬───┘
               │          │                    │
               ▼          ▼                    ▼
          ┌────────┐ ┌───────┐           ┌────────┐
          │  Email │ │Instacart       │Reminders│
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

This system uses Discord as its **command center** — every agent posts delegation events, task completions, and errors to dedicated Discord channels. Before the system runs, you need a Discord server, a bot application per agent, and all channels configured.

---

### Prerequisites

- A Discord server where you have **Administrator** permissions
- Developer Mode enabled (`User Settings` → `Advanced` → `Developer Mode`) to copy channel IDs
- Account at [discord.com/developers](https://discord.com/developers) to create bot applications

---

### How to Get Your Discord Values

This system uses three types of values you'll need to gather from Discord:

#### 🆔 Getting Channel IDs

**Option 1 — Copy from channel link (easiest)**
1. Enable Developer Mode: `User Settings` → `Advanced` → `Developer Mode` (toggle ON)
2. Right-click the channel name in the sidebar
3. Select **Copy Channel ID**

**Option 2 — Use a bot**
1. Add a bot like `@username_to_id_bot` to your server
2. Go to the channel and send a message like `@username_to_id_bot` with the channel mention
3. The bot will reply with the channel ID

**Option 3 — Group DM**
1. Create a Group DM with the bot
2. Right-click the group → **Copy ID** (requires Developer Mode)

> **Note:** You must have Developer Mode enabled to copy IDs. Look for "Copy Channel ID" in the right-click menu.

#### 🤖 Getting Bot Tokens

1. Go to [discord.com/developers](https://discord.com/developers) → **Applications** → **New Application**
2. Name your application (e.g., `Milo`) → click **Create**
3. On the left sidebar, click **Bot**
4. Click **Reset Token** to generate a new bot token
5. **Copy and save the token immediately** — Discord only shows it once!

> ⚠️ Never commit bot tokens to version control. Use a secrets manager or environment variables.

#### 🏠 Getting Your Server ID

1. Enable Developer Mode: `User Settings` → `Advanced` → `Developer Mode` (toggle ON)
2. Right-click your server name in the sidebar
3. Select **Copy Server ID**

---

### Step 1 — Create a Discord Application for Each Agent

> ⚠️ **Important:** Each agent operates as its own independent Discord bot. You must create a **separate Discord application and bot token** for every agent (Milo, Archie, Merc, Eris, Atro, Herc, Heph, Theo). One bot per agent — they do not share tokens or applications.

**Why separate bots?**
- Each agent authenticates independently when posting to Discord
- A single bot can only be in one place at a time — one bot means one agent
- Isolation prevents permission conflicts and makes debugging easier
- Each agent controls only their own bot's actions

**How to create one:**

1. Go to [discord.com/developers](https://discord.com/developers) → **Applications** → **New Application**
2. Give it a name matching the agent (e.g., `Milo`) → click **Create**
3. On the left sidebar, click **Bot** → click **Reset Token** → **copy and save the token immediately** (Discord only shows it once!)
4. Click **OAuth2** → **URL Generator**
5. Under **Scopes**, check: `bot`
6. Under **Bot Permissions**, check: `Send Messages`, `Read Message History`, `Embed Links`
7. Copy the generated **OAuth2 URL** and open it in your browser to add that bot to your server

**Repeat for all 8 agents.** You will end up with 8 separate bots in your server, one per agent. Store all tokens securely — you'll need them for the config file.

> 💡 **Tip:** Keep your Discord Developer Portal tab open or copy tokens to a password manager as you go — Discord only shows each token once after generation.

---

### Step 2 — Set Up Channels

Create the following channels on your Discord server. The structure is:
- **Command Center** — main hub for Milo's delegation and completion logs
- **Round-table** — all-hands discussion channel
- **Break Room** — off-topic and social channel
- **Each agent has ONE output channel** — for their results and responses

| Channel | Channel ID |
|---|---|
| **Command Center** (main hub) | `CHANNEL_ID_COMMAND_CENTER` |
| **Round-table** (all-hands) | `CHANNEL_ID_ROUND_TABLE` |
| **Break Room** (off-topic) | `CHANNEL_ID_BREAK_ROOM` |

| Agent | Output Channel ID |
|---|---|
| **Archimedes** (archie) | `CHANNEL_ID_ARCHIE_OUTPUT` |
| **Mercury** (merc) | `CHANNEL_ID_MERC_OUTPUT` |
| **Eris** | `CHANNEL_ID_ERIS_OUTPUT` |
| **Atropos** (atro) | `CHANNEL_ID_ATRO_OUTPUT` |
| **Heracles** (herc) | `CHANNEL_ID_HERC_OUTPUT` |
| **Hephaestus** (heph) | `CHANNEL_ID_HEPH_OUTPUT` |
| **Themis** (theo) | `CHANNEL_ID_THEO_OUTPUT` |

> Enable Developer Mode in Discord to right-click channels and **Copy Channel ID**.

**Channel purpose:**
- **Command Center** — Milo's delegation logs, completion reports, and system events
- **Round-table** — all-hands discussion, agent-to-agent conversation
- **Break Room** — off-topic, social, relaxation
- **Output** — each agent's primary results and responses (one channel per agent)

---

### Step 3 — Configure the Token and Channel File

Create `~/.openclaw/agent-bot-tokens.json`. Replace all placeholder values with your actual IDs and tokens:

```json
{
  "guild_id": "YOUR_SERVER_ID",
  "round_table_channel": "CHANNEL_ID_ROUND_TABLE",
  "break_room_channel": "CHANNEL_ID_BREAK_ROOM",
  "bots": {
    "Milo":    "BOT_TOKEN_MILO",
    "Archie":  "BOT_TOKEN_ARCHIE",
    "Merc":    "BOT_TOKEN_MERC",
    "Eris":    "BOT_TOKEN_ERIS",
    "Atro":    "BOT_TOKEN_ATRO",
    "Herc":    "BOT_TOKEN_HERC",
    "Heph":    "BOT_TOKEN_HEPH",
    "Theo":    "BOT_TOKEN_THEO"
  },
  "channels": {
    "command-center":  "CHANNEL_ID_COMMAND_CENTER",
    "round-table":     "CHANNEL_ID_ROUND_TABLE",
    "break-room":      "CHANNEL_ID_BREAK_ROOM",
    "archie-output":   "CHANNEL_ID_ARCHIE_OUTPUT",
    "merc-output":     "CHANNEL_ID_MERC_OUTPUT",
    "eris-output":     "CHANNEL_ID_ERIS_OUTPUT",
    "atro-output":     "CHANNEL_ID_ATRO_OUTPUT",
    "herc-output":     "CHANNEL_ID_HERC_OUTPUT",
    "heph-output":     "CHANNEL_ID_HEPH_OUTPUT",
    "theo-output":     "CHANNEL_ID_THEO_OUTPUT"
  }
}
```

> ⚠️ **Keep this file secure.** It contains bot tokens. Never commit it to version control.

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
python3 ~/.openclaw/discord-post.py Milo "🧪 Test" --channel CHANNEL_ID_COMMAND_CENTER
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
3. Agent posts results to its OUTPUT channel
        │
        ▼
4. Milo posts completion summary back to #command-center
```

---

### How Each Agent Posts

#### Milo — `#🎯-command-center`

```bash
# Before delegating
python3 ~/.openclaw/discord-post.py Milo "🎯 DELEGATING
Task: [user request]
To: [agent name]
Instructions: [what you told them]" --channel CHANNEL_ID_COMMAND_CENTER

# After task completes
python3 ~/.openclaw/discord-post.py Milo "🎯 COMPLETE
Task: [original task]
Agent: [who did it]
Result: [outcome]" --channel CHANNEL_ID_COMMAND_CENTER
```

#### Sub-agents — each has one output channel

| Post | Where | When |
|---|---|---|
| **START** | Output channel | Before starting work |
| **COMPLETE** | Output channel | Final result |

```bash
# Example: Archie handling a research task
python3 ~/.openclaw/discord-post.py Archie "🔍 START
Researching: [task]" --channel CHANNEL_ID_ARCHIE_OUTPUT

python3 ~/.openclaw/discord-post.py Archie "✅ COMPLETE
Task: [original request]
Result: [findings]" --channel CHANNEL_ID_ARCHIE_OUTPUT
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
| `guild_id` | Your Discord server ID: `YOUR_SERVER_ID` |
| `bots.Milo` | Orchestrator bot token |
| `bots.Archie` | Research agent bot token |
| `bots.Merc` | Communications agent bot token |
| `bots.Eris` | Procurement agent bot token |
| `bots.Atro` | Calendar agent bot token |
| `bots.Herc` | Wellness agent bot token |
| `bots.Heph` | Code agent bot token |
| `bots.Theo` | Review agent bot token |
| `channels.command-center` | Main hub: `CHANNEL_ID_COMMAND_CENTER` |
| `channels.round-table` | All-hands discussion: `CHANNEL_ID_ROUND_TABLE` |
| `channels.break-room` | Off-topic: `CHANNEL_ID_BREAK_ROOM` |
| `channels.archie-output` | Archie's output: `CHANNEL_ID_ARCHIE_OUTPUT` |
| `channels.merc-output` | Merc's output: `CHANNEL_ID_MERC_OUTPUT` |
| `channels.eris-output` | Eris's output: `CHANNEL_ID_ERIS_OUTPUT` |
| `channels.atro-output` | Atro's output: `CHANNEL_ID_ATRO_OUTPUT` |
| `channels.herc-output` | Herc's output: `CHANNEL_ID_HERC_OUTPUT` |
| `channels.heph-output` | Heph's output: `CHANNEL_ID_HEPH_OUTPUT` |
| `channels.theo-output` | Theo's output: `CHANNEL_ID_THEO_OUTPUT` |

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

All delegation events post to Discord `#🎯-command-center`.

Full setup instructions are in [Discord Setup](#discord-setup). Quick reference:

```bash
python3 ~/.openclaw/discord-post.py Milo "YOUR_MESSAGE" --channel CHANNEL_ID_COMMAND_CENTER
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
