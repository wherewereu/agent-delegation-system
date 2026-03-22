# Agent Delegation System - Requirements

## System Requirements

### Minimum Requirements
- **OS**: macOS 13+ or Linux (Ubuntu 20.04+)
- **RAM**: 4 GB available
- **Storage**: 500 MB free space
- **Network**: Stable internet connection for API calls

### Recommended Requirements
- **OS**: macOS 14+ or Linux (Ubuntu 22.04+)
- **RAM**: 8 GB available
- **Storage**: 1 GB free space
- **Network**: Low-latency connection (<100ms to API endpoints)

## Software Dependencies

### Core Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| OpenClaw | Latest | Agent orchestration framework |
| Node.js | 18+ | Runtime for OpenClaw |
| Git | 2.30+ | Version control |

### API Access
| Service | Required | Purpose |
|---------|----------|---------|
| MiniMax API | Yes | Primary AI model for agents |
| Telegram Bot API | Recommended | Primary communication channel |
| Discord API | Yes | Team command center |

### Optional Dependencies
| Dependency | Purpose |
|------------|---------|
| gh (GitHub CLI) | Repository management |
| Things 3 | Task management integration |
| Apple Reminders | Calendar integration |

## What Are OpenClaw Subagents?

This system uses **OpenClaw subagents** (also called *spawned agents*). These are not separate processes — they are **sessions spawned by the main orchestrator agent** using the `sessions_yield` tool.

Each subagent:
- Has its own `SKILL.md` defining its role, behavior, and rules
- Receives a specific task from the main agent (Milo)
- Operates within its own workspace context
- Returns results back to the orchestrator when complete

The main agent (Milo) classifies incoming requests and spawns the right subagent for the job. This keeps each agent focused and prevents prompt pollution.

## Configuration

### 1. OpenClaw Installation
```bash
npm install -g openclaw
openclaw setup
```

### 2. Subagent Setup

Each specialist subagent needs a `SKILL.md` skill file. Create a directory for each agent under your skills folder:

```bash
mkdir -p ~/.openclaw/skills/archie
mkdir -p ~/.openclaw/skills/merc
mkdir -p ~/.openclaw/skills/eris
# ... etc
```

See the **Setting Up Subagents** section in README.md for the full step-by-step guide.

### 3. Environment Variables
```bash
export MINIMAX_API_KEY="your-api-key"
export TELEGRAM_BOT_TOKEN="your-telegram-token"
export DISCORD_WEBHOOK_URL="your-webhook-url"
```

### 4. Discord Channels — One Per Agent

Each subagent has **one Discord output channel**. Additionally, three shared channels coordinate the team:

| Agent / Channel | Channel ID | Purpose |
|---|---|---|
| **Command Center** (Milo) | `1483891285822537740` | Delegation logs, completion reports, errors |
| **Archie** (Research) | `1483891301773480017` | Archie's task output |
| **Merc** (Communications) | `1483891383700820132` | Merc's task output |
| **Eris** (Procurement) | `1483891385458491402` | Eris's task output |
| **Atro** (Calendar) | `1483891386783629322` | Atro's task output |
| **Herc** (Health) | `1483891388184526919` | Herc's task output |
| **Heph** (Code) | `1483944411795816641` | Heph's task output |
| **Theo** (Review) | `1483944415985930300` | Theo's task output |
| **Round Table** | `1483982757523750942` | Multi-agent discussion |
| **Break Room** | `1485043346132045824` | Off-topic / social |

> **No logs or memory channels.** Each agent posts its output directly to its one output channel. The Command Center is the single source of delegation truth.

### 5. Directory Structure
```
~/.openclaw/
├── workspace/
│   ├── SOUL.md              # Main agent (Milo) persona
│   ├── AGENTS.md
│   └── memory/
├── agents/                  # Isolated agent state
│   ├── main/
│   ├── archie/
│   ├── merc/
│   └── ...                  # one per subagent
└── skills/                  # Subagent skill definitions
    ├── archie/
    │   └── SKILL.md
    ├── merc/
    └── ...
```

### 6. Inter-Agent Communication
Configure mesh relay at:
```
http://192.168.0.247:8500/messages/send
```

## Agent Specializations

| Agent | Role | Primary Skills |
|-------|------|----------------|
| Milo | Orchestrator (main agent) | Intent classification, routing, coordination, spawning subagents |
| Archie | Research subagent | Web search, fact-checking, information retrieval |
| Merc | Communications subagent | Email, messaging, social posting |
| Eris | Procurement subagent | Shopping, ordering, inventory |
| Atro | Calendar subagent | Scheduling, reminders, time management |
| Herc | Health subagent | Wellness tracking, nutrition, fitness |
| Heph | Code subagent | Programming, scripting, automation |
| Theo | Review subagent | Code review, quality assurance, verification |

## Deployment Checklist

- [ ] OpenClaw installed and configured
- [ ] All subagent skill files created (`SKILL.md` per agent)
- [ ] MiniMax API key configured
- [ ] Telegram bot token (if using Telegram)
- [ ] Discord bot tokens created for each agent
- [ ] Discord channels created: 1 per agent + Command Center + Round Table + Break Room
- [ ] `discord-post.py` script installed and tested
- [ ] Inter-agent mesh relay tested
- [ ] Test delegation flow completed

## Known Limitations

1. **Single orchestrator**: Milo must be online for delegation to work
2. **Sequential Heph → Theo**: Code review adds latency (no parallelization)
3. **API rate limits**: MiniMax rate limits apply per agent
4. **Context window**: Large conversations may lose delegation context

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not responding | Check skill file is loaded, restart agent |
| Delegation failing | Verify mesh relay connection |
| Classification errors | Adjust keyword weights in SPEC.md |
| API errors | Check API key validity and rate limits |
