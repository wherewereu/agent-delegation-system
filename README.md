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

All delegation events post to Discord `#🎯-command-center`:

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
