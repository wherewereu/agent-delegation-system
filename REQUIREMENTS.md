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
| Discord API | Optional | Team coordination |

### Optional Dependencies
| Dependency | Purpose |
|------------|---------|
| gh (GitHub CLI) | Repository management |
| Things 3 | Task management integration |
| Apple Reminders | Calendar integration |

## Configuration

### 1. OpenClaw Installation
```bash
npm install -g openclaw
openclaw setup
```

### 2. Agent Configuration
Each agent requires:
- `SOUL.md` - Persona definition
- `memory/` - Directory for memory files
- `IDENTITY.md` - Agent identity

### 3. Environment Variables
```bash
export MINIMAX_API_KEY="your-api-key"
export TELEGRAM_BOT_TOKEN="your-telegram-token"
export DISCORD_WEBHOOK_URL="your-webhook-url"
```

### 4. Directory Structure
```
~/.openclaw/
├── workspace/
│   ├── agents/
│   │   ├── milo/          # Orchestrator
│   │   ├── archie/        # Research agent
│   │   ├── merc/          # Communications agent
│   │   ├── eris/          # Procurement agent
│   │   ├── atro/          # Calendar agent
│   │   ├── herc/          # Health agent
│   │   ├── heph/          # Code agent
│   │   └── theo/          # Review agent
│   └── skills/
└── config/
```

### 5. Inter-Agent Communication
Configure mesh relay at:
```
http://192.168.0.247:8500/messages/send
```

## Agent Specializations

| Agent | Role | Primary Skills |
|-------|------|----------------|
| Milo | Orchestrator | Intent classification, routing, coordination |
| Archie | Research | Web search, fact-checking, information retrieval |
| Merc | Communications | Email, messaging, social posting |
| Eris | Procurement | Shopping, ordering, inventory |
| Atro | Calendar | Scheduling, reminders, time management |
| Herc | Health | Wellness tracking, nutrition, fitness |
| Heph | Code | Programming, scripting, automation |
| Theo | Review | Code review, quality assurance, verification |

## Deployment Checklist

- [ ] OpenClaw installed and configured
- [ ] All agent directories created with SOUL.md files
- [ ] MiniMax API key configured
- [ ] Telegram bot token (if using Telegram)
- [ ] Discord webhook configured (for command center)
- [ ] Inter-agent mesh relay tested
- [ ] Memory directories initialized
- [ ] Delegation triggers configured
- [ ] Test delegation flow completed

## Known Limitations

1. **Single Point of Failure**: Milo must be online for delegation
2. **No Native Load Balancing**: Agents handle one task at a time by default
3. **Context Window**: Large conversations may lose delegation context
4. **API Rate Limits**: MiniMax rate limits apply per agent

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent not responding | Check memory files and restart agent |
| Delegation failing | Verify mesh relay connection |
| Classification errors | Adjust keyword weights in SPEC.md |
| API errors | Check API key validity and rate limits |
