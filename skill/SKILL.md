# Agent Delegation Skill

## Metadata

| Field | Value |
|-------|-------|
| **Name** | agent-delegation |
| **Version** | 1.0.0 |
| **Description** | Enables automatic task routing from Milo to specialist agents based on intent classification |
| **Author** | Milo Blake |
| **Category** | orchestration |
| **Tags** | delegation, routing, multi-agent, orchestration |
| **Triggers** | delegation request, task routing, agent coordination |

## Overview

This skill enables Milo to automatically analyze incoming user requests and delegate tasks to the appropriate specialist agent without requiring manual routing decisions.

## Usage

### When to Use

Use this skill when:
- User submits a task that needs specialist handling
- A task requires research, email, shopping, calendar, health, coding, or review
- Cross-agent coordination is needed
- You need to verify which agent should handle a request

### How to Use

1. **Analyze the request** - Identify task type from user input
2. **Classify intent** - Match against trigger keywords
3. **Check availability** - Verify agent is available
4. **Delegate** - Route to appropriate specialist
5. **Monitor** - Track task completion
6. **Report** - Return results to user

## Intent Classification

### Trigger Keywords by Agent

| Agent | Keywords |
|-------|----------|
| Archie (Research) | research, find, look up, search, what is, who is, information |
| Merc (Communications) | email, inbox, unsubscribe, gmail, message, send, post |
| Eris (Procurement) | order, buy, instacart, amazon, grocery, purchase, shop |
| Atro (Calendar) | calendar, schedule, remind, event, appointment, invite |
| Herc (Health) | water, walking, diet, calories, health, sleep, weight, nutrition |
| Heph (Code) | code, build, fix, script, create, program, function, automation |
| Theo (Review) | review, check, verify, audit, test, validate, approve |

### Classification Confidence

| Score | Action |
|-------|--------|
| 0.7+ | Auto-delegate immediately |
| 0.4-0.69 | Delegate with monitoring |
| < 0.4 | Escalate to Milo for manual routing |

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
┌─────────────────┐
│ Intent Classify │
└──────┬──────────┘
    │
    ▼
┌─────────────────┐
│ Route to Agent  │
└──────┬──────────┘
    │
    ▼
┌─────────────────┐
│ Execute Task    │
└──────┬──────────┘
    │
    ▼
┌─────────────────┐
│ Verify (if Heph)│──► Theo Review
└──────┬──────────┘
    │
    ▼
┌─────────────────┐
│ Report Back     │
└─────────────────┘
```

## Scripts

### `delegate.sh`
Routes a task to the specified agent.

```bash
./delegate.sh <agent> <task_description> [priority]
```

### `classify-intent.sh`
Classifies a user request and returns recommended agent.

```bash
./classify-intent.sh "<user_request>"
```

### `check-agent.sh`
Checks if an agent is available.

```bash
./check-agent.sh <agent_name>
```

## Example Delegations

### Example 1: Research Task
```
User: "is it going to rain today?"
Classification: Research (Archie)
Delegation: Archie → web_search("weather today")
Result: "No rain today, 72°F sunny"
```

### Example 2: Calendar Task
```
User: "remind me to call mom at 5pm"
Classification: Calendar (Atro)
Delegation: Atro → create_reminder("call mom", 5pm)
Result: Reminder set for 5pm
```

### Example 3: Shopping Task
```
User: "order more coffee"
Classification: Shopping (Eris)
Delegation: Eris → instacart_add("coffee")
Result: Added to Instacart cart
```

### Example 4: Code Task with Review
```
User: "write a script to backup my files"
Classification: Code (Heph)
Delegation: Heph → write_script("backup.sh")
After completion:
    Theo reviews → APPROVED
Result: Script created and verified
```

## Configuration

### Agent Availability
Each agent has a max concurrent task limit:

| Agent | Max Concurrent |
|-------|---------------|
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
| Agent unavailable | Queue task, notify when agent free |
| Agent timeout | Retry up to 3 times, then escalate |
| Classification failure | Milo handles manually |
| Task rejected | Re-route or Milo handles |

## Memory Integration

Agents maintain memory via:
- `memory/YYYY-MM-DD.md` - Daily activity logs
- `MEMORY.md` - Long-term context
- Delegation history stored for learning

## Command Center Integration

All delegations are posted to Discord command center:
- Delegation start notifications
- Completion reports
- Error alerts
- Autonomous decisions

Channel: #⚒️-code-output (ID: 1483891285822537740)

## Skill Files

```
skill/
├── SKILL.md           # This file
└── scripts/
    ├── delegate.sh         # Route task to agent
    ├── classify-intent.sh  # Classify user request
    └── check-agent.sh      # Check agent availability
```

## Changelog

### v1.0.0 (2026-03-21)
- Initial release
- Basic intent classification
- 7 specialist agents
- Command center integration
