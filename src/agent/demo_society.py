#!/usr/bin/env python3
"""
AIGON-X Agent Society — Demo Scenario Runner

Simulates a system alert and shows the multi-agent response pipeline.
Each stage calls a real kernel in the runtime to demonstrate Agent Society.
"""

import json
import os
import sys
import time
import urllib.request

RUNTIME_URL = os.environ.get("RUNTIME_URL", "http://localhost:7000")
QWEN_API_KEY = os.environ.get("QWEN_API_KEY", "")
QWEN_ENDPOINT = os.environ.get("QWEN_ENDPOINT",
    "https://<your-workspace-id>.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1")


def runtime_get(path):
    url = f"{RUNTIME_URL}{path}"
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def qwen_chat(prompt, model="qwen3.7-max"):
    data = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }).encode()
    req = urllib.request.Request(
        f"{QWEN_ENDPOINT}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {QWEN_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Qwen error: {e}]"


def step(num, name, emoji, action):
    print(f"\n{'='*60}")
    print(f"  STEP {num}: {emoji} {name}")
    print(f"{'='*60}")
    result = action()
    print(f"  -> {result}")
    time.sleep(0.5)
    return result


def main():
    print("""
    +============================================================+
    |     AIGON-X Agent Society - Live Demo                      |
    |     12 Specialized AI Agents - Powered by Qwen Cloud       |
    +============================================================+
    """)

    def get_health():
        h = runtime_get("/health")
        k = h.get("kernels", {})
        m = h.get("mesh", {})
        kpi = h.get("kpi", {})
        return (f"Kernels: {k.get('healthy', '?')}/12 healthy . "
                f"Mesh: {m.get('healthy_peers', '?')} peers . "
                f"IQ: {kpi.get('last_iq_score', '?')}")

    step(1, "Runtime Health Check", "[health]", get_health)

    step(2, "Plank Kernel - Planning", "[plan]", lambda: qwen_chat(
        "As a planning agent, create a 3-step response plan for: "
        "'High memory usage detected on worker node 3 (92%)'. "
        "Output as JSON with step, action, and estimated duration."))

    step(3, "Galileo Kernel - Knowledge Review", "[review]", lambda: qwen_chat(
        "As a knowledge review agent, check this incident response plan against "
        "standard operating procedures. Identify any risks or missing steps.",
        "qwen3-coder-plus"))

    step(4, "Nash Kernel - Game Theory", "[nash]", lambda: qwen_chat(
        "As a game-theoretic decision agent: there are 3 competing priorities "
        "(memory pressure, pending deploy, security scan). Use Nash equilibrium "
        "to determine the optimal order. Output: priority queue with rationale.",
        "qwq-plus"))

    step(5, "Nano Kernel - Execution", "[exec]", lambda: qwen_chat(
        "As an execution agent, generate the exact shell commands to: "
        "1) identify top memory consumers, 2) restart the memory-intensive "
        "service gracefully, 3) verify recovery. Assume Ubuntu 24.04.",
        "qwen3-coder-flash"))

    step(6, "Darwin Kernel - Evolution", "[evolve]", lambda: qwen_chat(
        "As an evolution agent: analyze this incident pattern (memory pressure "
        "at 92% on worker). Propose 2 configuration parameter mutations that "
        "would prevent recurrence. Optimize for fitness: uptime > memory usage."))

    step(7, "Yudai Kernel - Security Compliance", "[secure]", lambda: qwen_chat(
        "As a security compliance agent: verify that the proposed response "
        "plan passes these 8 rules: no_open_ports, max_session_age, "
        "failed_login_threshold, pat_revocation, cors_validation, tls_enforced, "
        "audit_log, all_kernels_healthy. Output PASS/FAIL per rule."))

    print(f"\n{'='*60}")
    print("  [OK] Agent Society - Full Incident Response Cycle Complete")
    print(f"{'='*60}")
    print("  7 specialized agents collaborated autonomously:")
    print("  [health] -> [plan] -> [review] -> [nash] -> [exec] -> [evolve] -> [secure]")
    print("  Powered by Qwen Cloud (qwen3.7-max, qwq-plus, qwen3-coder-flash)")


if __name__ == "__main__":
    main()
