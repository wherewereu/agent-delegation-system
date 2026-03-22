# Agent Delegation System - Technical Specification

## What Are OpenClaw Subagents?

This system is built on **OpenClaw subagents** (spawned agents). An OpenClaw subagent is a session spawned by the main orchestrator agent using the `sessions_yield` tool. Each subagent:
- Has its own `SKILL.md` defining its role, behavior, and rules
- Receives a task prompt and context from the main agent
- Operates within its own workspace / skill context
- Returns results back to the orchestrator

The main agent (Milo) is always the entry point for user requests. It classifies the intent and spawns the appropriate subagent to handle the task.

## Intent Classifier Logic

### Overview
The intent classifier analyzes natural language input and determines the appropriate specialist subagent to handle the request.

### Classification Algorithm

```
Input: Raw user request (string)
Output: Agent assignment + confidence score

1. Preprocessing
   - Lowercase normalization
   - Remove punctuation
   - Tokenize into words

2. Keyword Matching
   - Check against trigger keyword dictionary
   - Score = number of matching keywords per category

3. Disambiguation Rules
   - If multiple categories score equally:
     - Check for compound requests ("email and calendar")
     - Default to highest-priority category
     - Escalate to human review if tie persists

4. Confidence Threshold
   - >= 0.7: Auto-delegate (spawn subagent immediately)
   - 0.4-0.69: Flag for review, still delegate
   - < 0.4: Escalate to Milo for manual routing
```

### Keyword Weighting
| Category | Primary Keywords | Weight |
|----------|-----------------|--------|
| Research | research, find, look up, search, what is, who is | 1.0 |
| Communications | email, inbox, unsubscribe, gmail, mail, message, send, post | 1.0 |
| Procurement | order, buy, instacart, amazon, grocery, purchase, shop | 1.0 |
| Calendar | calendar, schedule, remind, event, appointment | 1.0 |
| Health | water, walking, diet, calories, health, sleep, weight, nutrition | 1.0 |
| Code | code, build, fix, script, create, programming, function, automation | 1.0 |
| Review | review, check, verify, audit, test, validate, approve | 1.0 |

## Agent Routing Rules

### Spawning via sessions_yield

When Milo delegates, it calls `sessions_yield` with:
- `skill`: the subagent's skill name (e.g., "archie")
- `prompt`: the task description and context
- `label`: a session label for tracking

The subagent session is created, loads its `SKILL.md`, executes the task, and returns results to Milo.

### Routing Priority Matrix
```
┌─────────────┬──────────────────┬─────────────────┐
│   Agent     │   Specialization │   Max Concurrent│
├─────────────┼──────────────────┼─────────────────┤
│ Archie      │ Research         │ 3               │
│ Merc        │ Communications   │ 5               │
│ Eris        │ Procurement      │ 2               │
│ Atro        │ Calendar         │ 5               │
│ Herc        │ Health/Wellness  │ 3               │
│ Heph        │ Coding           │ 2               │
│ Theo        │ Code Review      │ 3               │
└─────────────┴──────────────────┴─────────────────┘
```

### Routing Flow
1. Classify intent → get agent category
2. Check agent availability (concurrent task limit)
3. Spawn subagent via `sessions_yield`
4. Monitor subagent completion
5. Return results to user

### Fallback Routing
| Primary Agent | Fallback Agent |
|--------------|----------------|
| Archie | Milo (manual) |
| Merc | Milo (manual) |
| Eris | Milo (manual) |
| Atro | Milo (manual) |
| Herc | Milo (manual) |
| Heph | Theo |
| Theo | Milo (manual) |

## Discord Channel Structure

Each OpenClaw subagent has **one output channel**. Three shared channels coordinate the whole team:

| Channel | Purpose |
|---------|---------|
| **Command Center** | Delegation logs, completion reports, errors (Milo posts here) |
| **Round Table** | Multi-agent discussion and coordination |
| **Break Room** | Off-topic and social chatter |

Subagent channels (one per agent):

| Agent | Channel ID | Purpose |
|-------|------------|---------|
| Milo (Command Center) | `YOUR_COMMAND_CENTER_CHANNEL_ID` | Milo's delegation output |
| Archie | `YOUR_ARCHIE_OUTPUT_CHANNEL_ID` | Archie's task output |
| Merc | `YOUR_MERC_OUTPUT_CHANNEL_ID` | Merc's task output |
| Eris | `YOUR_ERIS_OUTPUT_CHANNEL_ID` | Eris's task output |
| Atro | `YOUR_ATRO_OUTPUT_CHANNEL_ID` | Atro's task output |
| Herc | `YOUR_HERC_OUTPUT_CHANNEL_ID` | Herc's task output |
| Heph | `1483944411795816641` | Heph's task output |
| Theo | `1483944415985930300` | Theo's task output |
| Round Table | `1483982757523750942` | Multi-agent discussion |
| Break Room | `1485043346132045824` | Off-topic / social |

## Communication Protocols

### Inter-Agent Message Format
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
    "priority": "normal|urgent|low",
    "callback_channel": "discord"
  },
  "status": "pending|assigned|completed|failed"
}
```

### Delivery Guarantees
- **At-least-once delivery** for all agent messages
- **Retry policy**: 3 attempts with exponential backoff
- **Timeout**: 30 seconds for agent acknowledgment

### Discord Posting Rules
Every spawned agent posts to its own output channel. Milo's Command Center posts the delegation start and completion. This is the audit trail — **if it's not in Discord, it didn't happen**.

## Error Handling

### Error Categories

| Error Type | Detection | Response |
|------------|-----------|----------|
| Subagent timeout | No response in 30s | Re-queue or escalate |
| Agent unavailable | Max concurrent reached | Queue with priority |
| Classification failure | Confidence < 0.4 | Escalate to Milo |
| Communication failure | Message delivery failed | Retry 3x, then alert |
| Task rejection | Agent unable to complete | Re-route or escalate |

### Recovery Procedures

1. **Subagent Timeout**
   ```
   1. Increment retry counter
   2. If retries < 3: re-delegate to same agent
   3. If retries >= 3: route to fallback agent
   4. If no fallback: escalate to Milo
   ```

2. **Communication Failure**
   ```
   1. Log error with message_id
   2. Store message in dead-letter queue
   3. Retry on next heartbeat
   4. Alert if persistent (>5 failures)
   ```

3. **Fallback Exhaustion**
   ```
   1. Milo takes ownership of task
   2. Attempt manual resolution
   3. Report back to user with explanation
   ```

## Memory Architecture

Each subagent maintains its own memory via its workspace:

- `memory/YYYY-MM-DD.md` — Daily activity log
- `MEMORY.md` — Long-term context (subagent-specific)
- `SOUL.md` — Persona and behavior rules

Milo maintains:
- `memory/delegation-queue.md` — Pending tasks
- `memory/routing-log.md` — Delegation history

Discord Round Table channel serves as the human-visible coordination log for multi-agent discussions.

## Security Considerations

- Subagents only access authorized resources per their `SOUL.md` / `SKILL.md`
- No cross-agent data sharing without explicit context passed in the task prompt
- All external actions require user consent (except internal routing)
- Audit log maintained in Command Center for all delegations
- Discord tokens stored in `~/.openclaw/agent-bot-tokens.json` (not committed to repo)
