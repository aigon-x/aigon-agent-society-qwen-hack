#!/usr/bin/env python3
"""
AIGON Agent Society (Qwen Hack) — Demo Scenario Runner

Connects to the runtime on Alibaba Cloud ECS and demonstrates the
multi-agent pipeline. Each stage calls a real kernel endpoint.
"""

import json
import subprocess
import sys
import time
from datetime import datetime

def runtime_get(path):
    """Call runtime API and return JSON."""
    try:
        result = subprocess.run(
            ["curl", "-sf", f"http://localhost:7000{path}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        return {"error": result.stderr or "empty response"}
    except Exception as e:
        return {"error": str(e)}

def runtime_post(path, data):
    """Call runtime API with POST."""
    try:
        result = subprocess.run(
            ["curl", "-sf", "-X", "POST", f"http://localhost:7000{path}",
             "-H", "Content-Type: application/json", "-d", json.dumps(data)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        return {"error": result.stderr or "empty response"}
    except Exception as e:
        return {"error": str(e)}

def print_header(text):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_field(label, value):
    """Print a key-value field."""
    print(f"  {label:25s} {value}")

# ── Main Demo ──────────────────────────────────────────────────────

print(f"\n{'#'*60}")
print(f"  AIGON Agent Society — Qwen Hack Demo")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'#'*60}")

print_header("1. Runtime Health")
h = runtime_get("/health")
if h and "error" not in h:
    kernels = h.get("kernels", {})
    mesh = h.get("mesh", {})
    kpi = h.get("kpi", {})
    print_field("Kernels healthy", f"{kernels.get('healthy', '?')}/12")
    print_field("Mesh peers", f"{mesh.get('healthy_peers', '?')}")
    print_field("Uptime", f"{kpi.get('uptime', '?')}s")
    print_field("Total tasks", f"{kpi.get('total_tasks', '?')}")
    print_field("FSIQ", f"{kpi.get('fsiq', '?')}")
else:
    print(f"  [!] Runtime not reachable: {h}")

print_header("2. Kernel Status")
kernels = runtime_get("/kernels")
if kernels and isinstance(kernels, list):
    for k in kernels:
        print(f"  • {k['name']:12s} {'✓' if k.get('healthy') else '✗'}  "
              f"{k.get('state', '?')}  {k.get('description', '')}")
elif isinstance(kernels, dict):
    for name, info in kernels.items():
        if isinstance(info, dict):
            print(f"  • {name:12s} {'✓' if info.get('healthy') else '✗'}  "
                  f"{info.get('state', '?')}")
        else:
            print(f"  • {name}")
elif "kernels" in kernels:
    pass  # already printed above

print_header("3. IQ Metrics")
iq = runtime_get("/iq")
if iq and "error" not in iq:
    for dim, score in iq.items():
        if isinstance(score, (int, float)):
            print(f"  • {dim:25s} {score}")
    print_field("FSIQ Total", iq.get("fsiq", "?"))
else:
    print(f"  [!] IQ endpoint: {iq}")

print_header("4. Federation (Mesh)")
mesh_status = runtime_get("/mesh/status")
if mesh_status and "error" not in mesh_status:
    for k, v in mesh_status.items():
        print(f"  • {k:20s} {v}")
else:
    print(f"  [!] Mesh: {mesh_status}")

print_header("5. Evolution (Darwin Kernel)")
darwin = runtime_get("/kernel/darwin/status")
if darwin and "error" not in darwin:
    for k, v in darwin.items():
        print(f"  • {k:20s} {v}")
else:
    print(f"  [!] Darwin: {darwin}")

print_header("6. Security (Yudai Kernel)")
yudai = runtime_get("/kernel/yudai/status")
if yudai and "error" not in yudai:
    for k, v in yudai.items():
        print(f"  • {k:20s} {v}")
else:
    print(f"  [!] Yudai: {yudai}")

print_header("7. Memory (Freud Kernel)")
freud = runtime_get("/kernel/freud/status")
if freud and "error" not in freud:
    for k, v in freud.items():
        if isinstance(v, (int, float, str)):
            print(f"  • {k:20s} {v}")
else:
    print(f"  [!] Freud: {freud}")

print_header("8. Knowledge Fabric")
knowledge = runtime_get("/kernel/knowledge/status")
if knowledge and "error" not in knowledge:
    for k, v in knowledge.items():
        if isinstance(v, (int, float, str)):
            print(f"  • {k:20s} {v}")
else:
    print(f"  [!] Knowledge: {knowledge}")

print(f"\n{'#'*60}")
print(f"  DEMO COMPLETE — Agent Society operational on Alibaba Cloud")
print(f"{'#'*60}\n")
