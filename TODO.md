# Agent Delegation System - TODO

## Features to Implement

### High Priority
- [x] Basic intent classification with keyword matching
- [x] Discord command center integration (1 output channel per agent + Command Center + Round Table + Break Room)
- [x] OpenClaw subagent spawning via sessions_yield
- [x] Per-agent SKILL.md skill files
- [x] Discord posting script (discord-post.py)
- [ ] Implement confidence scoring threshold in intent classifier
- [ ] Add subagent availability checking before delegation
- [ ] Create dead-letter queue for failed messages
- [ ] Add priority levels (urgent/normal/low) to delegation requests
- [ ] Implement fallback routing when primary subagent is busy

### Medium Priority
- [ ] Add ML-based intent classification using MiniMax fine-tuning
- [ ] Create visual delegation dashboard
- [ ] Implement learning from delegation patterns (store success/failure)
- [ ] Add support for compound requests (multi-agent tasks)
- [ ] Create subagent health monitoring (uptime, task count)
- [ ] Round Table integration for multi-agent discussion

### Low Priority
- [ ] Implement load balancing across multiple instances of same subagent
- [ ] Add delegation analytics and reporting
- [ ] Create natural language configuration for routing rules
- [ ] Add multi-language support for intent classification

## Improvements

### Intent Classification
- [ ] Add fuzzy matching for keyword detection
- [ ] Implement context-aware classification (previous tasks)
- [ ] Add support for implicit intents (no keywords but implied)
- [ ] Improve disambiguation for overlapping keywords

### Subagent Communication
- [ ] Add message encryption for inter-agent messages via mesh relay
- [ ] Implement message batching for efficiency
- [ ] Add real-time status updates via WebSocket
- [ ] Create standardized error codes

### Reliability
- [ ] Add circuit breaker pattern for failing subagents
- [ ] Implement automatic subagent recovery
- [ ] Add task timeout with configurable durations
- [ ] Create rollback mechanism for failed tasks

### Observability
- [ ] Add structured logging (JSON format)
- [ ] Implement delegation metrics (success rate, latency)
- [ ] Create alert system for delegation failures
- [ ] Add distributed tracing across agents

## Testing

### Unit Tests
- [ ] Test intent classifier with various inputs
- [ ] Test keyword matching algorithm
- [ ] Test confidence scoring
- [ ] Test routing logic

### Integration Tests
- [ ] Test full delegation flow (Milo → Subagent → Response)
- [ ] Test subagent spawning via sessions_yield
- [ ] Test Discord channel posting per agent
- [ ] Test fallback routing
- [ ] Test timeout and retry behavior
- [ ] Test Round Table multi-agent discussion

### End-to-End Tests
- [ ] Test real user requests through full system
- [ ] Test with Telegram integration
- [ ] Test Discord command center posting
- [ ] Test subagent memory persistence across sessions
- [ ] Test Break Room off-topic channel

### Load Tests
- [ ] Test concurrent delegations
- [ ] Test subagent saturation (max concurrent tasks)
- [ ] Test mesh relay under load
- [ ] Test API rate limit handling

## Documentation

- [x] README.md with subagent setup guide
- [x] SPEC.md with architecture and channel structure
- [x] REQUIREMENTS.md with deployment checklist
- [x] SKILL.md for delegation skill
- [ ] Document each subagent's SKILL.md structure
- [ ] Create API reference for inter-agent messages
- [ ] Write deployment guide for adding new subagents
- [ ] Document troubleshooting procedures
- [ ] Create architecture diagrams

## Channel Structure (Implemented)

Each subagent has **1 output channel**. Three shared channels for team coordination:

| Channel | Status |
|---------|--------|
| Command Center (Milo) | ✅ Implemented |
| Archie output | ✅ Implemented |
| Merc output | ✅ Implemented |
| Eris output | ✅ Implemented |
| Atro output | ✅ Implemented |
| Herc output | ✅ Implemented |
| Heph output | ✅ Implemented |
| Theo output | ✅ Implemented |
| Round Table | ✅ Implemented |
| Break Room | ✅ Implemented |

> Logs and memory channels have been removed. Each agent posts output directly to its channel. Command Center is the single source of delegation truth.

## Future Enhancements

### v2.0 Roadmap
- [ ] Multi-tenant support (multiple users/teams)
- [ ] Custom subagent creation via UI
- [ ] Drag-and-drop workflow builder
- [ ] A/B testing for routing algorithms

### v3.0 Roadmap
- [ ] Federated subagents (run on different machines)
- [ ] Plugin system for custom subagent types
- [ ] Natural language query interface
- [ ] Predictive task routing
