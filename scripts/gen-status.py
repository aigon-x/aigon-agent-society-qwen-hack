#!/usr/bin/env python3
"""Generate AIGON Agent Society status page from live runtime health data."""
import json, subprocess, sys

def get_json(path):
    r = subprocess.run(["curl", "-sf", f"http://localhost:7000{path}"],
                       capture_output=True, text=True, timeout=5)
    return json.loads(r.stdout) if r.stdout else {}

d = get_json("/health")
iq = d.get("iq_test_battery", {})

ecs_id = subprocess.run(
    ["curl", "-s", "http://100.100.100.200/latest/meta-data/instance-id"],
    capture_output=True, text=True, timeout=3).stdout.strip()

region = subprocess.run(
    ["curl", "-s", "http://100.100.100.200/latest/meta-data/zone-id"],
    capture_output=True, text=True, timeout=3).stdout.strip()

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>AIGON Agent Society</title>
<style>
body {{ font-family: 'SF Mono','Courier New',monospace; background:#0a0a0f; color:#e0e0e0; padding:40px; max-width:900px; margin:auto; }}
h1 {{ color:#00d4aa; border-bottom:2px solid #00d4aa; padding-bottom:10px; }}
.card {{ background:#1a1a2e; border:1px solid #2a2a4e; border-radius:8px; padding:20px; margin:12px 0; }}
.green {{ color:#00ff88; }}
.blue {{ color:#00aaff; }}
table {{ width:100%; border-collapse:collapse; }}
td,th {{ padding:6px 10px; text-align:left; border-bottom:1px solid #2a2a4e; }}
.header {{ display:flex; justify-content:space-between; align-items:center; }}
.fsiq {{ font-size:48px; font-weight:bold; color:#00ff88; }}
.label {{ color:#666; font-size:12px; text-transform:uppercase; }}
</style></head><body>
<div class="header"><h1>🛸 AIGON Agent Society</h1><div><div class="fsiq">{iq.get('full_scale_iq',0):.0f}</div><div class="label">FSIQ</div></div></div>

<div class="card">
<h2>Runtime — Live on Alibaba Cloud</h2>
<table>
<tr><td>Instance</td><td>{ecs_id}</td></tr>
<tr><td>Region</td><td>{region}</td></tr>
<tr><td>Node ID</td><td class="blue">{d.get('node_id','?')}</td></tr>
<tr><td>Kernels</td><td class="green">{d.get('kernels',{}).get('healthy',0)}/12 Healthy</td></tr>
<tr><td>Uptime</td><td>{d.get('uptime_seconds',0)}s</td></tr>
<tr><td>Immune System</td><td class="green">{d.get('immune_system',{}).get('state','?')}</td></tr>
<tr><td>System Errors</td><td class="green">{d.get('system_errors',{}).get('total_errors',0)}</td></tr>
<tr><td>Entropy</td><td>{d.get('entropy',{}).get('total_entropy',0):.4f}</td></tr>
</table>
</div>

<div class="card">
<h2>12 Kernels · Agent Society</h2>
<table>
<tr><th>Kernel</th><th>Ticks</th><th>SLA</th><th>Status</th><th>Details</th></tr>
"""
for k in d.get("kernel_health", []):
    det = k.get("details", {})
    detail = ""
    if "generation" in det: detail = f"Gen {det.get('engine_stats',[{}])[0].get('generation',0)} pop {det.get('engine_stats',[{}])[0].get('population',0)}"
    elif "compliance" in det: detail = f"8 rules {'✅' if all(c['passed'] for c in det['compliance']) else '❌'}"
    elif "decisions_made" in det: detail = f"{det['decisions_made']} decisions"
    elif "total_reviews" in det: detail = f"{det['total_reviews']} reviews"
    elif "lts_entries" in det: detail = f"{det['memory_entries']} mem entries"
    elif "plans_cached" in det: detail = f"{det['plans_cached']} plans cached"
    elif "workers" in det: detail = f"{det['workers']} workers, {det['total_tasks']} tasks"
    else: detail = "active"
    html += f'<tr><td>{k["kernel_name"]}</td><td>{k["ticks_total"]}</td><td>{k["sla_compliance_pct"]:.0f}%</td><td class="green">{k["status"]}</td><td>{detail}</td></tr>\n'

html += f"""</table></div>
<div class="card">
<h2>IQ Profile</h2>
<table>
<tr><td>Working Memory</td><td class="green">{iq.get('working_memory',0):.3f}</td>
<td>Processing Speed</td><td class="green">{iq.get('processing_speed',0):.3f}</td></tr>
<tr><td>Logical Reasoning</td><td class="green">{iq.get('logical_reasoning',0):.3f}</td>
<td>Knowledge Integration</td><td class="green">{iq.get('knowledge_integration',0):.3f}</td></tr>
<tr><td>Resilience</td><td class="green">{iq.get('resilience',0):.3f}</td>
<td>Experience</td><td class="green">{iq.get('experience',0):.3f}</td></tr>
</table>
</div>
<div class="card" style="font-size:12px;color:#666;text-align:center">
<p>Intel Xeon Platinum 8369B · 7.4GB RAM · 40GB SSD · Alibaba Cloud Linux 4</p>
<p>Powered by qwen3.7-max via Qwen Cloud MaaS (ap-southeast-1)</p>
<p>AIGON-X Runtime v2 · Agent Society Track · Qwen Cloud Hackathon 2026</p>
</div></body></html>"""

with open("/opt/aigon-hack/status.html", "w") as f:
    f.write(html)
print("OK")
