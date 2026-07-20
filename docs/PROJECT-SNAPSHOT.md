# AIGON Agent Society — Project Snapshot

**Generated:** 2026-07-20 10:30 EDT
**Deadline:** 2026-07-20 17:00 EDT
**Status:** Submitted ✅

## Links

| Co | URL |
|----|-----|
| Devpost | https://devpost.com/software/aigon-agent-society-multi-agent-cognitive-runtime |
| YouTube | https://youtu.be/NUJoCnZwdvk |
| GitHub | https://github.com/aigon-x/aigon-agent-society-qwen-hack |
| Dashboard | https://prod-aigon.taila6760f.ts.net/ |
| Health | https://prod-aigon.taila6760f.ts.net/api/health |

## Infrastructure

| Node | IP | Rola |
|------|----|------|
| PROD | 100.99.59.100 (prod-aigon) | Główny runtime + dashboard |
| Public | 38.242.215.113 → DNAT na PROD | Publiczny ingress |

## Assets on PROD

`100.99.59.100:/home/sniegul/dashboard/assets/`

- `dashboard.html` — live dashboard (42 KB)
- `demo-video-en.mp4` — final video EN (13 MB)
- `demo-video-multi.mp4` — video 3 audio + 3 subs (23 MB)
- `narration_en.mp3`, `narration_pl.mp3`, `narration_cn.mp3`
- `subs_en.srt`, `subs_pl.srt`, `subs_cn.srt`
- `screenshot-devpost-*.png` — 3 screenshoty z wideo
- `screenshot-dashboard*.png` — dashboard screenshots
- `architecture.png` — diagram architektury
- `alibaba-proof.png` — dowód Qwen Cloud

## Key Scripts

| Script | Opis |
|--------|------|
| `scripts/gen-dash.py` | Generuje dashboard HTML (42 KB) |
| `scripts/render-video.py` | Renderuje wideo (4740 frames, 10 scen) |
| `scripts/gen-tts.py` | ElevenLabs TTS (EN Cornelius, PL Piotr) |
| `scripts/gen-tts-cn.py` | ElevenLabs CN (Cornelius Sage) |
| `scripts/gen-subs.py` | Generuje SRT dla 3 języków |
| `scripts/deploy-ecs.sh` | Deploy na Alibaba Cloud ECS |

## Qwen Cloud

- **Endpoint:** `ws-h3ayxryayp3b7ad5.ap-southeast-1.maas.aliyuncs.com`
- **Region:** ap-southeast-1 (Singapur)
- **Modele:** qwen3.7-max, qwq-plus, qwen-vl-max, text-embedding-v4
- **Tokens:** 106,000+ inference tokens

## Key Metrics (live)

- IQ 185 FSIQ / 179 Extended
- 12/12 kernels healthy
- 140,000+ system ticks
- 11,500+ Darwin generations
- 106,000+ inference tokens
- 0 errors, 100% SLA

## Devpost Content

- **Title:** AIGON Agent Society — Multi-Agent Cognitive Runtime
- **Pitch:** "12 specialized AI kernels running in production since Feb 2026 on a bare-metal mesh. Built with Qwen Cloud. IQ 185. Zero failures. Not a demo — a production society."
- **Built with:** 20 tags (Rust, Qwen Cloud, Axum, Tokio, PostgreSQL, etc.)
- **Try it out:** Dashboard, GitHub, Health endpoint
- **Gallery:** 13 images (screenshots, architecture, alibaba proof)

## Remaining Tasks

- [ ] Wrzucić LinkedIn post (Blog Post Prize)
- [ ] Dodać napisy PL/CN na YouTube
- [ ] Dodać audio PL/CN na YouTube
