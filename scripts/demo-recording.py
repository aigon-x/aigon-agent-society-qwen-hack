#!/usr/bin/env python3
"""Interactive demo script for Qwen Hack submission."""
import json, urllib.request, sys, time

RUNTIME = "http://100.99.59.100:8090"
DASH = "http://100.99.59.100:8090"

def fetch(path):
    r = urllib.request.Request(RUNTIME + "/api/" + path.lstrip("/"))
    with urllib.request.urlopen(r, timeout=5) as resp:
        return json.loads(resp.read())

def slow_print(text, delay=0.03):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

def pause(sec=2):
    time.sleep(sec)

def section(title):
    print(f"\n{'#'*60}")
    print(f"# {title}")
    print(f"{'#'*60}\n")
    pause(1)

# ── Intro ──
slow_print("AIGON Agent Society — Qwen Cloud Hackathon Demo")
slow_print("Runtime v2 · 12-Kernel Society · IQ Battery · Qwen Cloud API")
pause(2)

# ── 1. Runtime Health ──
section("1. Runtime Health — 12 kernel society")
slow_print("Fetching runtime health...")
d = fetch("/health")
ks = d.get("kernels", {})
fsiq = d.get("iq_test_battery", {}).get("full_scale_iq", 0)
slow_print(f"  ✓ Boot phase: {d.get('boot_phase', '?')}")
slow_print(f"  ✓ Kernels: {ks.get('healthy', 0)}/{ks.get('total', 0)} healthy")
slow_print(f"  ✓ FSIQ: {fsiq:.1f}")
slow_print(f"  ✓ Uptime: {d.get('uptime_seconds', 0)}s")
pause(3)

# ── 2. IQ Battery ──
section("2. IQ Battery — 6 cognitive dimensions")
iq = d.get("iq_test_battery", {})
dims = ["working_memory", "processing_speed", "logical_reasoning",
        "knowledge_integration", "resilience", "experience"]
for dim in dims:
    v = iq.get(dim, 0)
    bar = "█" * int(v * 20) + "░" * (20 - int(v * 20))
    slow_print(f"  {dim.replace('_',' '):22s} {v:.3f}  {bar}")
pause(3)

# ── 3. Dashboard ──
section("3. Live Dashboard")
slow_print(f"Dashboard URL: {DASH}/")
slow_print("Real-time metrics: kernels, IQ, evolution, security, mesh")
with urllib.request.urlopen(DASH + "/", timeout=5) as resp:
    content = resp.read().decode()
    if "AIGON Agent Society" in content:
        slow_print("  ✓ Dashboard reachable and serving")
pause(3)

# ── 4. Kernel List ──
section("4. Kernel Society")
kernels = d.get("kernel_health", [])
names = ["nano", "curie", "planck", "freud", "galileo", "yairoslaw",
         "hawking", "turing", "knowledge", "nash", "darwin", "yudai"]
for i, (name, k) in enumerate(zip(names, kernels)):
    status = k.get("status", "?")
    ticks = k.get("ticks_total", 0)
    sla = k.get("sla_compliance_pct", 0)
    icon = "🟢" if status == "Healthy" else "🟡" if status == "Degraded" else "🔴"
    slow_print(f"  {icon} {name:12s}  {status:10s}  {ticks:>8,} ticks  {sla:>5.0f}% SLA", 0.01)
pause(3)

# ── 5. Yudai Security ──
section("5. Yudai Security — 8 compliance rules")
yudai = kernels[11].get("details", {})
compliance = yudai.get("compliance", [])
for c in compliance:
    icon = "✅" if c.get("passed") else "❌"
    slow_print(f"  {icon}  {c.get('rule','?').replace('_',' ')}", 0.02)
pause(3)

# ── 6. Darwin Evolution ──
section("6. Darwin Evolution Engine")
darwin = kernels[10].get("details", {})
es = (darwin.get("engine_stats") or [{}])[0]
slow_print(f"  Generations:  {es.get('generation', 0):,}")
slow_print(f"  Population:   {es.get('population', 0):,}")
slow_print(f"  Best fitness: {es.get('best_fitness', 0):.4f}")
slow_print(f"  Diversity:    {es.get('diversity', 0):.4f}")
pause(3)

# ── 7. 15 Breakthroughs ──
section("7. 15 Breakthroughs")
bts = [
    "Compiled Runtime — native ms cold start",
    "12-Kernel Society — 12 consensus-driven organisms",
    "Mesh Federation — MAIPS, Raft CRDT, TLS",
    "Cognitive ISA — 6 instructions, all behavior",
    "Virtual Context Memory — 64-bit L1/L2/L3",
    "Knowledge Fabric — Entity, Evidence, Timeline",
    "Darwin Evolution — genetic optimization",
    "Immune System — entropy + neutralization",
    "Time Machine — append-only temporal replay",
    "IQ Battery — FSIQ with 6 cognitive dimensions",
    "Yudai Security — 8 rules, every tick",
    "Cognitive Trace — full audit trail",
    "Semantic ABI — provider contract",
    "Runtime Physics — 7 cognition laws",
    "Runtime Biology — organism model",
]
for i, bt in enumerate(bts, 1):
    slow_print(f"  {i:02d}. {bt}", 0.008)
pause(2)

# ── Outro ──
section("OUTRO")
slow_print("Built with Qwen Cloud MaaS • Alibaba ECS • Qwen models")
slow_print("GitHub: aigon-x/aigon-agent-society-qwen-hack")
slow_print("Live:   http://100.99.59.100:8090/")
slow_print("\nThank you!")
pause(2)
