# Scout Skills Inventory
**Agent:** Scout | **Role:** Market Research | **Date:** 2026-03-25

---

## ✅ INSTALLED SKILLS

### Research & Search
| Skill | Status | Purpose |
|-------|--------|---------|
| `search` | ✅ ready | Privacy-preserving web search (SearXNG + Brave fallback) |
| `gemini` | ✅ ready | Gemini CLI for Q&A, summaries, generation |
| `openai-whisper` | ✅ ready | Local speech-to-text (no API key) |

### Sales & Marketing
| Skill | Status | Purpose |
|-------|--------|---------|
| `sales-prompts` | ✅ ready | SMB prospect research, cold outreach, proposals |
| `marketing-prompts` | ✅ ready | Content calendars, blog posts, SEO, competitor analysis |

### Multimodal (NEW — installed today)
| Skill | Status | Purpose |
|-------|--------|---------|
| `minimax-multimodal-toolkit` | ✅ installed | TTS, voice cloning/design, music, video (text/image-to-video), image generation |

**What minimax-multimodal-toolkit adds (vs existing skills):**
- `search` already covers web search ✅
- `openai-whisper` already covers local STT ✅
- `gemini` already covers Q&A/summaries ✅
- **NEW coverage:** TTS, voice cloning, music generation, video generation, image generation — all via MiniMax APIs (China: `api.minimaxi.com`, Global: `api.minimax.io`)

### Communication & Productivity
| Skill | Status | Purpose |
|-------|--------|---------|
| `imsg` | ✅ ready | iMessages/SMS on macOS |
| `bear-notes` | ✅ ready | Bear notes management |
| `apple-notes` | ✅ ready | Apple Notes via memo CLI |
| `obsidian` | ✅ ready | Obsidian vault operations |
| `things-mac` | ✅ ready | Things 3 task management |

### Infrastructure
| Skill | Status | Purpose |
|-------|--------|---------|
| `docker` | ✅ ready | Docker on Titan (.247) |
| `cloudflare` | ✅ ready | Cloudflare Tunnels & DNS |
| `github` | ✅ ready | GitHub PRs, issues, CI |
| `gh-issues` | ✅ ready | GitHub issue → PR workflow |

### Missing Skills (NOT installed)
| Skill | Status | Notes |
|-------|--------|-------|
| `openai-whisper-api` | ✗ missing | Cloud STT via OpenAI API (vs local) |
| `sag` (ElevenLabs TTS) | ✗ missing | ElevenLabs voice — could complement MiniMax TTS |
| `cloudflare-pages` | ✗ missing | Cloudflare Pages deploys — Flume's frontend deployment (not Vercel) |
| `railway` | ✗ missing | Railway/Render deploys — needed for backend |

---

## 📁 RESEARCH FILE INVENTORY

**Location:** `~/flume/research/`

### Agent Hosting Research (⚠️ HEAVILY DUPLICATED — 7 versions)
| File | Lines | Notes |
|------|-------|-------|
| `AGENT-HOSTING.md` | 625 | Main doc |
| `AGENT-HOSTING-FINAL-REVIEW.md` | 590 | Final review version |
| `AGENT-HOSTING-AUDIT.md` | 402 | Audit pass |
| `AGENT-HOSTING-COMPETITIVE.md` | 383 | Competitive analysis |
| `AGENT-HOSTING-REVIEW-R2.md` | 374 | Round 2 review |
| `AGENT-HOSTING-GO-NO-GO.md` | 154 | Decision doc |
| `AGENT-HOSTING-UX-RESEARCH.md` | 417 | UX research |

> **Recommendation:** Consolidate into one canonical version (`AGENT-HOSTING-FINAL.md`) and archive or delete the other 6.

### OpenClaw Architecture
| File | Lines | Notes |
|------|-------|-------|
| `OPENCLAW-ARCHITECTURE.md` | 1528 | Largest doc — comprehensive |

### API & Keys
| File | Lines | Notes |
|------|-------|-------|
| `API-KEYS-GETTING-STARTED.md` | 308 | + PDF version (64KB) |
| `REVERSE-PROXY-SETUP.md` | 457 | Infrastructure setup |

### Market & Brand
| File | Lines | Notes |
|------|-------|-------|
| `MARKET-REPORT.md` | 364 | Market analysis |
| `BRAND.md` | 441 | Brand guidelines |

### AI Vertical Research
| File | Lines | Notes |
|------|-------|-------|
| `ai-voice-agents-deep.md` | 496 | Voice agents deep-dive |
| `ai-course-monetization.md` | 417 | Course monetization |
| `trade-contractor-pain-points.md` | 441 | Trade contractor market |

### ClawCon AI Research
| File | Lines | Notes |
|------|-------|-------|
| `CLAWCON-AI-CHANNEL.md` | 233 | AI channel strategy |
| `CLAWCON-AI-VIDEO-RESEARCH.md` | 126 | Video research |

**Total research files:** 16 markdown files, 1 PDF

---

## 📁 LEADS FILE INVENTORY

**Location:** `~/flume/leads/`

### Primary Leads Data
| File | Size | Notes |
|------|------|-------|
| `LEADS-DEEP-ENRICHED-1000.md` | 371KB | **Primary 1000 leads file** ✅ consistent naming |
| `LEADS-ENRICHED.md` | 13KB | Partial enrichment |

### JSON Data Files
| File | Size | Notes |
|------|------|-------|
| `all_businesses_merged.json` | 81KB | ⚠️ likely a superset of all_businesses_final |
| `all_businesses_final.json` | 77KB | Final merged list |
| `bbb_with_emails.json` | 65KB | BBB data with emails |
| `bbb_raw.json` | 59KB | Raw BBB scrape |
| `bbb_clean.json` | 42KB | Cleaned BBB data |

> **Duplication:** `all_businesses_merged.json` (81KB) vs `all_businesses_final.json` (77KB) — merged is likely a superset. Consolidate to one.

### Outreach Materials
| File | Size | Notes |
|------|------|-------|
| `emails-Springtown-2026-03-25.md` | 16KB | Draft emails |
| `raw-directories-Springtown-2026-03-25.md` | 20KB | Raw directory listings |
| `cold-outreach-drafts-2026-03-25.md` | 3.9KB | Cold outreach drafts |
| `cold-call-script.md` | 7.4KB | Cold call script |
| `competitor-analysis-2026-03-25.md` | 12KB | Competitor analysis |
| `trade-businesses-Springtown-2026-03-25.md` | 12KB | Trade business list |
| `venue-options-2026-03-25.md` | 8.6KB | Venue options |

**Total leads files:** 14 files

---

## 🔍 SCOUT WORKSPACE

**Location:** `~/.openclaw/workspace/agents/scout/`

Subdirectories found:
- `AGENTS.md`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`, `TOOLS.md`, `USER.md` — agent config files
- `experiments/`, `ideas/`, `leads/`, `memory/`, `research/`, `skills/`, `workspace/` — workspace dirs
- `leads/` subdirectory contains additional research files (see below)

### Scout Leads Subdirectory (`scout/leads/`)
| File | Notes |
|------|-------|
| `ideaforge/` | Subdirectory |
| `API-DISCOVERY-FRESH.md` | |
| `API-INVENTORY-COMPLETE-2026-03-25.md` | |
| `ai-workshop-market-2026-03-25.md` | |
| `api-inventory-2026-03-25.md` | |
| `data-archive-plan-2026-03-25.md` | |
| `ftwdao-2026-03-25.md` | |
| `local-leads-2026-03-25.md` | |
| `trade-ai-market-2026-03-25.md` | |

---

## 🚨 GAPS IN RESEARCH TOOLKIT

### Critical Gaps
1. **No dedicated competitor monitoring skill** — no scheduled tracking of competitors' pricing, features, or blog posts
2. **No SEO research skill** — no dedicated keyword research, SERP analysis, or backlink tracking
3. **No CRM integration** — leads live in JSON/MD files, no connection to a CRM for pipeline management
4. **No email validation skill** — `bbb_with_emails.json` likely has unvalidated emails

### Medium Gaps
5. **No social listening skill** — no Twitter/social monitoring for market signals
6. **No trend detection** — no automated news/RSS monitoring for niche trend detection
7. **No lead scoring** — the 1000 enriched leads have no scoring/ranking beyond enrichment data

### Nice-to-Have
8. **`sag`** (ElevenLabs TTS) not installed — could complement `minimax-multimodal-toolkit` for voice content
9. **`openai-whisper-api`** not installed — cloud STT option if local Whisper fails
10. **`cloudflare-pages`** / **`railway`** not installed — needed when Scout needs to deploy landing pages for market testing

---

## 📋 ACTION ITEMS

1. **[Tyler/Ty]** Consolidate 7x AGENT-HOSTING*.md files into one canonical version — delete intermediates
2. **[Tyler/Ty]** Resolve `all_businesses_merged.json` vs `all_businesses_final.json` — pick one, trash the other
3. **[Scout]** Move scout leads subdirectory content to `~/flume/leads/` or document why it stays separate
4. **[Scout]** Consider installing `sag` (ElevenLabs TTS) as complement to MiniMax for voice content
5. **[Scout]** Consider installing `cloudflare-pages` for rapid landing page deployment during market testing (Flume uses Cloudflare Pages, NOT Vercel)

---

*Scout — Market Research Agent | Flume SaaS Factory*
