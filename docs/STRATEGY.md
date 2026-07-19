# Qwen Hack — Winning Strategy

## Project: AIGON-X Agent Society

**Track:** Agent Society
**Deadline:** Monday, July 20, 2026 @ 5:00 PM EDT
**Team:** Jakub Sniegocki (solo)

---

## 1. Why Agent Society

AIGON-X Runtime v2 is a **12-kernel multi-agent cognitive OS** running on a **4-node mesh** with:
- **Nano** — task execution engine (200 workers, 44K+ tasks)
- **Curie** — cognitive tick / steady-state reasoning
- **Planck** — planning & goal management
- **Freud** — memory (LTS, session, Hermes bridge)
- **Galileo** — knowledge & review
- **Yairoslaw** — distributed consensus (Raft CRDT)
- **Hawking** — fact/confidence system
- **Turing** — specification verification
- **Knowledge** — multi-source knowledge fabric
- **Nash** — game-theoretic decision making
- **Darwin** — evolutionary self-improvement
- **Yudai** — security & compliance scanning

This is **not a demo** — it's a production system already running in HA. The hackathon asks for "Agent Society" and we literally have one.

## 2. What We Submit

A working **Agent Society platform** deployed on Alibaba Cloud, where multiple specialized AI agents (kernels) collaborate autonomously: plan, reason, remember, negotiate, evolve, and self-heal.

### Core Demo: "AI Incident Response Team"
- Agent 1 (Planck) receives a system alert
- Agent 2 (Nano) spawns diagnostic tasks
- Agent 3 (Galileo) reviews findings against knowledge rules
- Agent 4 (Nash) decides response priority
- Agent 5 (Darwin) proposes improvement
- Agent 6 (Yudai) ensures compliance
- All coordinated via Yairoslaw consensus

### Key Differentiators
| Feature | AIGON-X | Typical Entry |
|---------|---------|---------------|
| Architecture | 12 specialized kernels | Single agent loop |
| Memory | Freud LTS + Hermes bridge | In-context only |
| Consensus | Raft CRDT via mesh | None |
| Evolution | Darwin genetic optimization | Static |
| Security | Yudai compliance scanner | None |
| IQ | 188 FSIQ measured | Undefined |
| Self-healing | Immune system + drift detection | Manual |

## 3. Technical Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Alibaba Cloud ECS                        │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │  Load Balancer│───▶│  Runtime v2  │── Qwen API calls ──▶│
│  │  (SLB)        │    │  (4 node     │                      │
│  └──────────────┘    │   mesh)      │◀─────────────────────│
│                      └──────┬───────┘                      │
│                             │                               │
│              ┌──────────────┴──────────────┐                │
│              │         Qwen Cloud MaaS      │                │
│              │  qwen3.7-max · qwq-plus ·    │                │
│              │  qwen-vl-max · embedding-v4  │                │
│              └─────────────────────────────┘                │
└────────────────────────────────────────────────────────────┘
```

### Deployment
- **Compute:** Alibaba Cloud ECS (Ubuntu 24.04)
- **Runtime:** Rust binary (cross-compiled, ~15MB)
- **AI:** Qwen Cloud MaaS API (compatible-mode)
- **Storage:** In-memory + optional RDS (PostgreSQL)
- **Demo UI:** Minimal web console (Ink/React or static HTML)

## 4. Timeline (24h sprint)

| Phase | Time | Task |
|-------|------|------|
| **NOW** | Sun eve | Plan, structure, research |
| **Phase 1** | ~4h | Adapt runtime for standalone Alibaba deploy |
| **Phase 2** | ~3h | Build demo scenario + web UI |
| **Phase 3** | ~2h | Deploy to Alibaba ECS, verify |
| **Phase 4** | ~2h | Record 3-min demo video |
| **Phase 5** | ~2h | Write description, architecture diagram |
| **Phase 6** | ~1h | Submit on Devpost |
| **Buffer** | ~8h | Overnight for YouTube processing |

## 5. Submission Checklist

- [ ] **Backend screenshot** — Runtime running on Alibaba ECS (`htop`, `/health`)
- [ ] **Public repo** — github.com/your-org/qwen-hack with MIT license
- [ ] **3-min demo video** — YouTube, public, no login required
- [ ] **Architecture diagram** — SVG/PNG included
- [ ] **Track:** Agent Society selected
- [ ] **All teammates** — solo, N/A
- [ ] **Text description** — What / Who / How
- [ ] **Qwen Cloud** — in description + "Built With" section
- [ ] **Eligible country** — Poland ✅

## 6. Demo Video Script (3 min)

**0:00-0:30** — "This is AIGON-X Agent Society, a multi-agent cognitive runtime running on Alibaba Cloud with 12 specialized AI agents collaborating autonomously."

**0:30-1:30** — Show the agent society in action: alert comes in → Planck plans → Nano executes → Galileo validates → Nash negotiates priority → Darwin evolves.

**1:30-2:00** — Show the runtime health dashboard: 12 kernels healthy, IQ score, self-healing immune system.

**2:00-2:30** — Show federation: 4-node mesh across Alibaba Cloud, consensus protocol (Yairoslaw), quorum.

**2:30-3:00** — "Built with Qwen Cloud — qwen3.7-max for reasoning, qwq-plus for deep analysis, and our open-source Rust runtime. Check the repo for details."

## 7. Technical Requirements

### For Alibaba Cloud deploy
- Rust cross-compile for `x86_64-unknown-linux-gnu` or `aarch64-unknown-linux-gnu`
- Minimal Dockerfile (~15MB binary)
- SLB config or direct port exposure on :7000
- Health endpoint for screenshot verification

### Qwen API Integration
- Chat completions: `qwen3.7-max` (primary), `qwq-plus` (deep reasoning)
- Vision: `qwen-vl-max` (if needed)
- Embeddings: `text-embedding-v4`

## 8. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Alibaba Cloud region/setup issues | Test credentials NOW |
| YouTube processing delay | Record and upload early |
| Runtime build failures | Use existing PROD binary first |
| API rate limits | Use flash models for non-critical calls |
| Repo setup delays | Fork existing aigon-x-new, strip irrelevant parts |
