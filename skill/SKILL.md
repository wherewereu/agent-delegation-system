# Agent Delegation Skill

## Metadata

| Field | Value |
|-------|-------|
| **Name** | agent-delegation |
| **Version** | 1.2.0 |
| **Description** | Enables automatic task routing from Milo (main orchestrator) to specialist OpenClaw subagents based on intent classification |
| **Author** | Milo Blake |
| **Category** | orchestration |
| **Tags** | delegation, routing, multi-agent, orchestration, subagent, spawned-agent |
| **Triggers** | delegation request, task routing, agent coordination |

## Overview

This skill enables Milo (the main orchestrator agent) to automatically analyze incoming user requests and spawn the appropriate specialist subagent to handle the task — without manual routing decisions.

## What Are OpenClaw Subagents?

The specialist agents (Archie, Merc, Eris, etc.) are **OpenClaw subagents** (also called *spawned agents*). They are not separate programs — they are sessions created by Milo using the `sessions_yield` tool. Each subagent:
- Has its own `SKILL.md` defining its role, behavior, and rules
- Receives a task from Milo with context and instructions
- Posts its output to its own Discord channel
- Returns results to Milo when complete

Milo (the main agent) is the orchestrator. All user requests come to Milo first. Milo classifies the intent, spawns the right subagent, and delivers the result.

## Usage

### When to Use

Use this skill when:
- User submits a task that needs specialist handling
- A task requires research, email, shopping, calendar, health, coding, or review
- Cross-subagent coordination is needed
- You need to verify which subagent should handle a request

### How to Use

1. **Analyze the request** — Identify task type from user input
2. **Classify intent** — Match against trigger keywords
3. **Check availability** — Verify subagent is available
4. **Spawn subagent** — Use `sessions_yield` to hand off the task
5. **Monitor** — Track subagent completion
6. **Report** — Return results to user

## Intent Classification

### Trigger Keywords by Subagent

| Subagent | Keywords |
|----------|----------|
| Archie (Research) | research, find, look up, search, what is, who is, information |
| Merc (Communications) | email, inbox, unsubscribe, gmail, message, send, post, linkedin |
| Eris (Procurement) | order, buy, instacart, amazon, grocery, purchase, shop |
| Atro (Calendar) | calendar, schedule, remind, event, appointment, invite |
| Herc (Health) | water, walking, diet, calories, health, sleep, weight, nutrition |
| Heph (Code) | code, build, fix, script, create, program, function, automation |
| Theo (Review) | review, check, verify, audit, test, validate, approve |

### Classification Confidence

| Score | Action |
|-------|--------|
| 0.7+ | Auto-spawn subagent immediately |
| 0.4-0.69 | Spawn with monitoring |
| < 0.4 | Milo handles manually |

## Delegation Flow

```
User Request
    │
    ▼
┌─────────────┐
│ Milo Analyzes│
└──────┬──────┘
    │
    ▼
┌─────────────────────┐
│ Intent Classify     │
└──────┬──────────────┘
    │
    ▼
┌─────────────────────┐
│ Spawn Subagent      │  ← sessions_yield
│ (Archie, Merc, etc) │
└──────┬──────────────┘
    │
    ▼
┌─────────────────────┐
│ Subagent Executes   │
│ Posts to its channel │
└──────┬──────────────┘
    │
    ▼
┌─────────────────────┐
│ Verify (if Heph)    │──► Theo Review
└──────┬──────────────┘
    │
    ▼
┌─────────────────────┐
│ Milo Reports Back   │
└─────────────────────┘
```

## Discord Channels — One Per Subagent

Each subagent has **one output channel**. Three shared channels coordinate the team:

| Channel | ID | Purpose |
|---------|-----|---------|
| **Command Center** (Milo) | `1483891285822537740` | Delegation logs, completions, errors |
| **Archie** (Research) | - | Archie's task output |
| **Merc** (Communications) | - | Merc's task output |
| **Eris** (Procurement) | - | Eris's task output |
| **Atro** (Calendar) | - | Atro's task output |
| **Herc** (Health) | - | Herc's task output |
| **Heph** (Code) | `1483944411795816641` | Heph's task output |
| **Theo** (Review) | `1483944415985930300` | Theo's task output |
| **Round Table** | `1483982757523750942` | Multi-agent discussion |
| **Break Room** | `1485043346132045824` | Off-topic / social |

> No logs or memory channels. Each subagent posts its output directly to its single channel.

## ⚠️ DISCORD POSTING RULES — MANDATORY FOR ALL AGENTS

### Milo — Command Center (#🎯-command-center, ID: 1483891285822537740)
Post to command center BEFORE delegating ANY task to ANY agent.
Post AFTER the task is complete with the result.

```bash
python3 /Users/justinedelano/.openclaw/discord-post.py Milo "YOUR_MESSAGE" --channel 1483891285822537740
```

Required format:
```
🎯 DELEGATING
Task: [what Justine asked for]
To: [agent name]
Instructions: [what you told them]

🎯 COMPLETE
Task: [original task]
Agent: [who did it]
Result: [outcome]
```

### Sub-agents — Your output channel
Every agent MUST post to its own Discord channel:
- START of task: what you are about to do
- END of task: what you did and the result
- ERRORS: what went wrong and what you tried

The discord-post.py script works from ANY context (Telegram, iMessage, cron).
It is a direct Discord API call — channel spawn context does not affect it.

### Hard rule: If it's not in Discord, it didn't happen.
Justine cannot see what you're doing without Discord logs.
Milo cannot supervise without Discord logs.
No exceptions. No "I forgot." Log everything.

### Command Center Posting (Milo)

```bash
# Before spawning a subagent
python3 /Users/justinedelano/.openclaw/discord-post.py Milo "🎯 DELEGATING
Task: [user request]
To: [subagent name]
Instructions: [what you told them]" --channel 1483891285822537740

# After subagent completes
python3 /Users/justinedelano/.openclaw/discord-post.py Milo "🎯 COMPLETE
Task: [original task]
Agent: [who did it]
Result: [outcome]" --channel 1483891285822537740
```

## Subagent Output Posting

Each subagent posts to its own channel:

```bash
# Start
python3 /Users/justinedelano/.openclaw/discord-post.py <AgentName> "🔍 START
Task: [what you're doing]" --channel <agent-channel-id>

# Complete
python3 /Users/justinedelano/.openclaw/discord-post.py <AgentName> "✅ COMPLETE
Task: [original request]
Result: [what you did/found]" --channel <agent-channel-id>

# Errors
python3 /Users/justinedelano/.openclaw/discord-post.py <AgentName> "❌ ERROR
Task: [original request]
Error: [what went wrong]
Tried: [what you attempted]" --channel <agent-channel-id>
```

## Scripts

### `delegate.sh`
Routes a task to the specified subagent via mesh relay.

```bash
./delegate.sh <agent> <task_description> [priority]
```

### `classify-intent.sh`
Classifies a user request and returns the recommended subagent.

```bash
./classify-intent.sh "<user_request>"
```

### `check-agent.sh`
Checks if a subagent is available.

```bash
./check-agent.sh <agent_name>
```

## Example Delegations

### Example 1: Research Task
```
User: "is it going to rain today?"
Classification: Research (Archie, confidence: 0.85)
Milo spawns Archie → Archie web_searches weather
Result: "No rain today, 72°F sunny"
```

### Example 2: Calendar Task
```
User: "remind me to call mom at 5pm"
Classification: Calendar (Atro, confidence: 0.92)
Milo spawns Atro → Atro creates reminder
Result: Reminder set for 5pm
```

### Example 3: Shopping Task
```
User: "order more coffee"
Classification: Procurement (Eris, confidence: 0.88)
Milo spawns Eris → Eris adds to Instacart
Result: Added to Instacart cart
```

### Example 4: Code Task with Review
```
User: "write a script to backup my files"
Classification: Code (Heph, confidence: 0.90)
Milo spawns Heph → Heph writes script
After completion:
    Milo spawns Theo → Theo reviews
Result: Script created and verified APPROVED
```

## Configuration

### Subagent Availability
Each subagent has a max concurrent task limit:

| Subagent | Max Concurrent |
|----------|----------------|
| Archie | 3 |
| Merc | 5 |
| Eris | 2 |
| Atro | 5 |
| Herc | 3 |
| Heph | 2 |
| Theo | 3 |

### Priority Levels
- **urgent**: Immediate routing, interrupt queue
- **normal**: Standard routing, FIFO within priority
- **low**: Background processing, lowest priority

## Error Handling

| Error | Response |
|-------|----------|
| Subagent unavailable | Queue task, notify when agent free |
| Subagent timeout | Retry up to 3 times, then escalate |
| Classification failure (< 0.4) | Milo handles manually |
| Task rejected | Re-route or Milo handles |

## Adding a New Subagent

1. **Create the skill file** at `~/.openclaw/skills/<name>/SKILL.md`
2. **Create a Discord output channel** for the new subagent
3. **Add the bot token** to `~/.openclaw/agent-bot-tokens.json`
4. **Add routing keywords** to the intent classifier
5. **Test** — Milo can now spawn this subagent via `sessions_yield`

## Skill Files

```
skill/
├── SKILL.md              # This file
└── scripts/
    ├── delegate.sh       # Route task to subagent via mesh relay
    ├── classify-intent.sh # Classify user request → recommended subagent
    └── check-agent.sh    # Check subagent availability
```

## Changelog

### v1.2.0 (2026-03-21)
- Updated Discord posting rules with correct channel IDs and script path
- Added hard rule: "If it's not in Discord, it didn't happen"
- Added error posting format for subagents
- Made Command Center channel ID concrete: 1483891285822537740

### v1.1.0 (2026-03-21)
- Updated channel structure: 1 output channel per subagent + Command Center + Round Table + Break Room
- Removed logs and memory channels
- Added OpenClaw subagent context throughout
- Clarified spawning via `sessions_yield`

### v1.0.0 (2026-03-21)
- Initial release
- Basic intent classification
- 7 specialist subagents
- Command center integration
