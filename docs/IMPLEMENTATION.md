# Implementation Plan

Track: **Agent Society**
Target: Deploy AIGON-X Runtime v2 on Alibaba Cloud ECS, integrated with Qwen Cloud MaaS.

---

## Phase 1: Prepare Runtime for Alibaba Deploy

### 1.1 Create standalone binary config
Build a minimal runtime-v2 profile with:
- All 12 kernels enabled
- Qwen Cloud API as primary LLM backend
- Compact config (no need for full mesh HA on demo)

### 1.2 Cross-compile for server
```bash
# Build release binary
cd /opt/aigon-x-new/runtime-v2
cargo build --release --bin aigon-runtime

# Strip for size (~15MB expected)
strip target/release/aigon-runtime
```

### 1.3 Create Dockerfile
```dockerfile
FROM ubuntu:24.04 AS runtime
COPY --from=builder aigon-runtime /usr/local/bin/
EXPOSE 7000
ENTRYPOINT ["aigon-runtime"]
```

## Phase 2: Qwen Cloud Integration

### 2.1 Configure runtime to use Qwen API
```toml
[llm]
provider = "openai-compatible"
api_url = "https://<your-workspace-id>.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
api_key = "${QWEN_API_KEY}"
model = "qwen3.7-max"
```

### 2.2 Add fallback models
- Primary: `qwen3.7-max` — reasoning & planning
- Flash: `qwen3-coder-flash` — quick code/exec tasks
- Deep: `qwq-plus` — complex analysis
- Embeddings: `text-embedding-v4` — memory RAG

## Phase 3: Demo Scenario

### 3.1 Agent Society demo script
Build a script that triggers a multi-agent incident response:
1. Inject simulated system alert
2. Planck creates resolution plan
3. Galileo reviews against knowledge rules
4. Nash negotiates priority
5. Nano executes tasks in parallel
6. Darwin proposes optimization
7. Yudai signs off on compliance

### 3.2 Web console (minimal)
Simple HTML dashboard showing:
- Runtime health (12/12 kernels)
- Agent society activity log
- IQ score
- Mesh status

## Phase 4: Alibaba Cloud Deploy

### 4.1 ECS setup
- Region: ap-southeast-1 (matching Qwen endpoint)
- Instance: ecs.g7.xlarge (4vCPU, 16GB) or similar
- OS: Ubuntu 24.04 LTS
- Security group: allow :7000 (management), :8080 (UI)

### 4.2 Deploy
```bash
scp aigon-runtime root@<ECS_IP>:/usr/local/bin/
ssh root@<ECS_IP>
# Run as service or Docker
```

### 4.3 Verify
```bash
curl http://<ECS_IP>:7000/health
```

## Phase 5: Demo Video

Topics to cover:
1. Agent Society concept — 12 specialized agents
2. Live demo — incident response workflow
3. Health dashboard — IQ 188, all kernels healthy
4. Mesh federation — 4-node consensus
5. Qwen Cloud integration

## Phase 6: Submission Materials

1. Architecture diagram (SVG)
2. Text description (who/what/how)
3. Backend screenshot
4. Public repo with LICENSE
5. Video uploaded to YouTube
6. Devpost submission filled
