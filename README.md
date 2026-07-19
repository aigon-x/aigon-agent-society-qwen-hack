# Qwen Hack — AIGON-X @ Qwen Cloud Global AI Hackathon

**Track:** Agent Society
**Deadline:** July 20, 2026 @ 5:00 PM EDT
**Team:** Solo (Jakub Sniegocki)

## What

AIGON-X Agent Society — a production multi-agent cognitive runtime with **12 specialized AI agents** (kernels) collaborating autonomously. Deployed on Alibaba Cloud, powered by Qwen Cloud MaaS.

## Who

Built on AIGON-X Runtime v2 — 67 crates, 12-kernel architecture, 4-node mesh federation. Already running in production on bare metal. This submission ports it to Alibaba Cloud ECS.

## How

Each kernel is a specialized agent:
- **Nano** (execution) · **Curie** (cognition) · **Planck** (planning) · **Freud** (memory)
- **Galileo** (knowledge) · **Yairoslaw** (consensus) · **Hawking** (facts)
- **Turing** (verification) · **Knowledge** (fabric) · **Nash** (decisions)
- **Darwin** (evolution) · **Yudai** (security)

Integrated with Qwen Cloud via `qwen3.7-max`, `qwq-plus`, and `text-embedding-v4`.

## Built With

- Qwen Cloud (qwen3.7-max, qwq-plus, qwen-vl-max, text-embedding-v4)
- Rust (Axum, Tokio, Serde)
- Alibaba Cloud ECS
- Docker

## Links

- **Alibaba Cloud endpoint:** `https://ws-h3ayxryayp3b7ad5.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1`
- **Demo video (3 min):** https://github.com/aigon-x/aigon-agent-society-qwen-hack/releases/download/demo-v1/demo-video.mp4

## Structure

```
qwen-hack/
├── README.md
├── CHECKLIST.md       ← submission tracking
├── docs/
│   ├── STRATEGY.md    ← winning strategy
│   └── IMPLEMENTATION.md ← build steps
├── src/
│   ├── backend/       ← Rust runtime integration
│   ├── frontend/      ← Web console
│   └── agent/         ← Agent society demo
├── infra/
│   ├── docker/        ← Container config
│   └── alibaba/       ← ECS deploy scripts
├── assets/
│   ├── img/
│   └── diagrams/
└── scripts/
```
