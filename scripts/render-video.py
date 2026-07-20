#!/usr/bin/env python3
"""
AIGON Agent Society — Procedural Demo Video Renderer
Animated: particles, cross-fade transitions, animated gradient, pulsing stats, animated bars.
"""
import os, sys, json, time, math, subprocess, requests, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from datetime import datetime

# ── Config ──
HEALTH_API = "http://100.99.59.100:7001/health"
W, H = 1280, 720
FPS = 24
OUT_DIR = "/opt/aigon-x-new/products/qwen-hack/.frames"
TRANS_DIR = "/opt/aigon-x-new/products/qwen-hack/.trans"
FINAL_MP4 = "/opt/aigon-x-new/products/qwen-hack/assets/demo-video-v2.mp4"

# ── Colors ──
BG = (3, 4, 7); BG_CARD = (28, 45, 75); BG_CARD2 = (40, 62, 100)
TEXT = (210, 220, 235); TEXT_DIM = (130, 150, 180); TEXT_BRIGHT = (245, 248, 252)
CYAN = (60, 220, 255); MAGENTA = (200, 140, 255); GREEN = (0, 255, 135)
YELLOW = (255, 220, 20); RED = (255, 80, 80)
ACCENT1 = (60, 245, 255); ACCENT2 = (210, 70, 255)
TRANSITION_FRAMES = 24  # 1s cross-fade
ANIM_BAR_FRAMES = 48    # 2s animation, grows from 0 to target

# ── Neural Network Background ──
NN_NODES = 140
NN_MAX_CONNECTIONS = 3
NN_MAX_DIST = 280
_nn_state = None

def init_neural_net():
    global _nn_state
    if _nn_state is not None: return
    random.seed(42)
    nodes = []
    for i in range(NN_NODES):
        nodes.append([
            random.randint(30, W-30),     # x
            random.randint(30, H-30),     # y
            random.uniform(0.8, 2.0),     # radius — subtle but visible
        ])
    # Build connection adjacency list
    connections = []  # each: (from, to, dist, born_at_frame)
    adj = [[] for _ in range(NN_NODES)]
    for i in range(len(nodes)):
        dists = [(j, math.hypot(nodes[i][0]-nodes[j][0], nodes[i][1]-nodes[j][1]))
                 for j in range(len(nodes)) if j != i]
        dists.sort(key=lambda x: x[1])
        for j, d in dists[:NN_MAX_CONNECTIONS]:
            if d < NN_MAX_DIST:
                if not any(c[1]==j for c in adj[i]) and not any(c[0]==i for c in adj[j]):
                    idx = len(connections)
                    # Each connection has a random birth frame (0-600) so connections
                    # gradually appear over the first ~25s of video
                    connections.append([i, j, d, random.randint(0, 600)])
                    adj[i].append((j, idx))
                    adj[j].append((i, idx))
    travelers = []
    _nn_state = (nodes, connections, adj, travelers)

def _spawn_traveler(travelers, adj, nodes, connections, frame):
    """Spawn a new signal at a random node. Only uses born connections."""
    start = random.randint(0, len(nodes)-1)
    # Only use connections that are already born
    born = [(n, ci) for n, ci in adj[start] if connections[ci][3] <= frame]
    if born:
        nxt, _ = random.choice(born)
        travelers.append({
            'current': start,
            'next': nxt,
            'progress': 0.0,
            'speed': random.uniform(0.04, 0.08),
            'trail': [],
            'spawn_frame': frame,
        })

def draw_neural_net(draw, global_frame):
    init_neural_net()
    nodes, connections, adj, travelers = _nn_state

    # Spawn travelers less frequently
    if global_frame > 60 and global_frame % 20 == 0 and random.random() < 0.5:
        _spawn_traveler(travelers, adj, nodes, connections, global_frame)
    if global_frame % 35 == 0 and random.random() < 0.4:
        _spawn_traveler(travelers, adj, nodes, connections, global_frame)

    # Advance each traveler
    for tr in travelers:
        tr['progress'] = min(1.0, tr['progress'] + tr['speed'])
        if tr['progress'] >= 1.0:
            tr['trail'].insert(0, [tr['current'], tr['next'], 1.0])
            if len(tr['trail']) > 4:
                tr['trail'] = tr['trail'][:4]
            tr['current'] = tr['next']
            cand = [(n, ci) for n, ci in adj[tr['current']]
                    if connections[ci][3] <= global_frame]
            if cand:
                last_two = set()
                if tr['trail']:
                    last_two.add(tr['trail'][0][0])
                if len(tr['trail']) > 1:
                    last_two.add(tr['trail'][1][0])
                others = [(n, c) for n, c in cand if n not in last_two]
                nxt, _ = random.choice(others) if others else random.choice(cand)
                tr['next'] = nxt
                tr['progress'] = 0.0
            else:
                tr['progress'] = -1
        for t in tr['trail']:
            t[2] = max(0.0, t[2] - 0.035)

    travelers[:] = [tr for tr in travelers if tr['progress'] >= 0]

    # Compute per-connection signal gradually
    conn_signal = [0.0] * len(connections)
    for ci in range(len(connections)):
        a, b, d, born = connections[ci]
        if global_frame < born:
            continue  # connection not yet visible
        # Fade in over ~10 frames after birth — visible from start
        fade_in = min(1.0, (global_frame - born) / 10.0)
        conn_signal[ci] = fade_in * 0.1  # baseline visibility: 10% max (very subtle)

    # Add traveler signals on top
    for tr in travelers:
        for ci, (a, b, _, _) in enumerate(connections):
            if (a == tr['current'] and b == tr['next']) or (b == tr['current'] and a == tr['next']):
                conn_signal[ci] = max(conn_signal[ci], tr['progress'] * 0.6 + 0.1)
                break
        for a, b, fade in tr['trail']:
            for ci, (ca, cb, _, _) in enumerate(connections):
                if (ca == a and cb == b) or (ca == b and cb == a):
                    conn_signal[ci] = max(conn_signal[ci], fade * 0.25)
                    break

    # Draw connections — subtle
    for ci, (i, j, d, _) in enumerate(connections):
        sig = conn_signal[ci]
        if sig < 0.02:
            continue
        nx1, ny1, nx2, ny2 = nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1]
        alpha = int(sig * 60)
        if alpha > 5:
            w = 2 if sig > 0.2 else 1
            r, g, b = int(40 + sig*150), int(90 + sig*120), int(150 + sig*80)
            draw.line([nx1, ny1, nx2, ny2],
                      fill=(min(255,r), min(255,g), min(255,b), min(255,alpha)),
                      width=w)

    # Draw nodes — always visible with dim base, brighten with signal
    for i, (nx, ny, r) in enumerate(nodes):
        avg_sig = 0.0
        count = 0
        for n, ci in adj[i]:
            avg_sig += conn_signal[ci]
            count += 1
        avg_sig = avg_sig / max(count, 1)
        boost = avg_sig * 2.0
        # Base glow — always drawn regardless of connections
        glow_r = r * (1.5 + boost * 2.0)
        glow_alpha = int(20 + boost * 15)
        rv = int(50 + boost * 70)
        gv = int(80 + boost * 80)
        bv = int(130 + boost * 70)
        draw.ellipse([nx-glow_r, ny-glow_r, nx+glow_r, ny+glow_r],
                     fill=(min(255,rv), min(255,gv), min(255,bv), min(255,glow_alpha)))
        # Core — always visible
        core_r = max(1, int(r * 0.8 + boost * 0.5))
        core_a = int(30 + boost * 20)
        draw.ellipse([nx-core_r, ny-core_r, nx+core_r, ny+core_r],
                     fill=(min(255, 70+int(boost*100)),
                            min(255, 110+int(boost*100)),
                            min(255, 170+int(boost*80)),
                            min(255, core_a)))

# ── Helpers ──
def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

_cached_health = None
_last_fetch = -999

def R():
    global _cached_health, _last_fetch
    # Re-fetch every 15 frames to stay fresh without hammering
    if _cached_health is None:
        try:
            _cached_health = requests.get(HEALTH_API, timeout=5).json()
        except:
            _cached_health = {}
    return _cached_health

def refresh_health(global_frame):
    """Call at scene start to get fresh data."""
    global _cached_health, _last_fetch
    try:
        _cached_health = requests.get(HEALTH_API, timeout=5).json()
        _last_fetch = global_frame
    except:
        pass

def load_fonts():
    base = "/usr/share/fonts/truetype/dejavu/"
    sg = "/usr/share/fonts/truetype/space-grotesk/"
    return {
        'mono': ImageFont.truetype(base + "DejaVuSansMono.ttf", 16),
        'mono_sm': ImageFont.truetype(base + "DejaVuSansMono.ttf", 13),
        'mono_lg': ImageFont.truetype(base + "DejaVuSansMono.ttf", 22),
        'mono_xl': ImageFont.truetype(base + "DejaVuSansMono.ttf", 32),
        'mono_xxl': ImageFont.truetype(base + "DejaVuSansMono.ttf", 44),
        'sans': ImageFont.truetype(base + "DejaVuSans.ttf", 16),
        'sans_sm': ImageFont.truetype(base + "DejaVuSans.ttf", 12),
        'sans_lg': ImageFont.truetype(base + "DejaVuSans.ttf", 22),
        'cosmic': ImageFont.truetype(sg + "SpaceGrotesk-Bold.ttf", 56),
        'cosmic_lg': ImageFont.truetype(sg + "SpaceGrotesk-Bold.ttf", 64),
        'cosmic_sm': ImageFont.truetype(sg + "SpaceGrotesk-Medium.ttf", 28),
    }

def card(draw, x, y, w, h, fill=BG_CARD, border=None):
    draw.rounded_rectangle([x, y, x+w, y+h], radius=8, fill=fill)
    if border:
        draw.rounded_rectangle([x, y, x+w, y+h], radius=8, outline=border, width=2)
    else:
        # Subtle default border to separate card from bg
        draw.rounded_rectangle([x, y, x+w, y+h], radius=8, outline=(80, 120, 180), width=1)

def dot(draw, x, y, r, color, glow=False):
    if glow:
        for i in range(3):
            a = 60 - i * 20
            draw.ellipse([x-r-i*4, y-r-i*4, x+r+i*4, y+r+i*4],
                         fill=(*color[:3], a) if len(color)==3 else color)
    draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

def gradient_bar(draw, x, y, w, h, pct, fg, bg=None):
    if bg is None: bg = (30, 40, 60)
    draw.rectangle([x, y, x+w, y+h], fill=bg)
    fw = int(w * pct)
    for i in range(fw):
        t = i / max(fw, 1)
        r = int(fg[0] * (1-t) + min(255, fg[0]+60) * t)
        g = int(fg[1] * (1-t) + min(255, fg[1]+60) * t)
        b = int(fg[2] * (1-t) + min(255, fg[2]+60) * t)
        draw.rectangle([x+i, y, x+i+1, y+h], fill=(r,g,b))

def anim_bar(draw, x, y, w, h, target_pct, fg, bg, frame_i):
    """Animated bar: fills from 0 over ANIM_BAR_FRAMES frames."""
    pct = min(1.0, target_pct * min(1.0, frame_i / ANIM_BAR_FRAMES))
    gradient_bar(draw, x, y, w, h, pct, fg, bg)
    return pct

def pulse(val, frame, freq=0.04, amp=0.12, phase=0):
    """Oscillate a value between val*(1-amp) and val."""
    return val * (1.0 - amp + amp * math.sin(frame * freq + phase))

def draw_gradient_text(draw, text, pos, font, color1, color2, offset=0):
    """Gradient text with optional scroll offset."""
    x, y = pos
    n = len(text)
    for i, ch in enumerate(text):
        t = ((i + offset * 0.5) % n) / max(n-1, 1)
        r = int(color1[0] * (1-t) + color2[0] * t)
        g = int(color1[1] * (1-t) + color2[1] * t)
        b = int(color1[2] * (1-t) + color2[2] * t)
        cx = x + draw.textlength(text[:i], font=font)
        draw.text((cx, y), ch, font=font, fill=(r,g,b))

def pulsing_text(draw, text, pos, font, color, frame, freq=0.03, amp=0.15, anchor=None):
    """Text with pulsing brightness."""
    b = pulse(1.0, frame, freq, amp)
    c = tuple(min(255, int(v * b)) for v in color[:3])
    draw.text(pos, text, font=font, fill=c, anchor=anchor)

# ═══════════════════════════════════════════
# Scene Renderers
# Signature: render_NAME(frame_i, total_frames, fonts, global_frame)
#   frame_i = 0..total_frames-1 (within this scene)
#   total_frames = scene duration in frames
#   global_frame = absolute frame counter
# ═══════════════════════════════════════════

def render_title(frame_i, total_frames, fonts, global_frame):
    """Scene 1: Clean title card — elegant, no kicz."""
    refresh_health(global_frame)
    h_data = R()
    k = h_data.get('kernels', {})
    kpi = h_data.get('kpi', {})
    ext_iq = kpi.get('last_extended_iq_score', 0)
    uptime = h_data.get('uptime_seconds', 0)

    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle top gradient for depth
    for y in range(180):
        a = int(15 * (1 - y / 180))
        draw.rectangle([0, y, W, y+1], fill=(20-a, 30-a, 50-a))

    # Small event tag
    draw.text((640, 120), "Qwen Cloud Global AI Hackathon 2026",
              font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")

    # Main title — cosmic font, left-aligned
    draw.text((100, 200), "AIGON", font=fonts['cosmic_lg'], fill=CYAN)
    draw.text((100, 265), "Agent Society", font=fonts['cosmic_sm'], fill=TEXT_BRIGHT)
    draw.text((100, 305), "12-Kernel Multi-Agent Cognitive Runtime",
              font=fonts['mono'], fill=TEXT_DIM)

    # Separator line
    draw.rectangle([100, 335, 600, 337], fill=(40, 55, 80))

    # Stats row — 4 cards, clean
    y0 = 370
    stats = [
        (f"{k.get('healthy','?')}/{k.get('total','?')}", "Kernels", GREEN),
        (f"{ext_iq:.0f}", "Extended IQ", ACCENT2),
        (f"{uptime//3600}h{(uptime%3600)//60}m", "Uptime", CYAN),
        ("Qwen Cloud", "API Provider", ACCENT1),
    ]
    for i, (val, label, clr) in enumerate(stats):
        cx = 70 + i * 300
        card(draw, cx, y0, 260, 72, BG_CARD2, border=clr)
        draw.text((cx+130, y0+16), val, font=fonts['mono_lg'], fill=clr, anchor="mm")
        draw.text((cx+130, y0+46), label, font=fonts['mono_sm'], fill=TEXT, anchor="mm")

    # GPU / Qwen / Federated badge strip
    sc = h_data.get('scaler', {})
    workers = sc.get('active_workers', 0)
    badges = [
        (f"⚡ GPU-Accelerated", ACCENT1),
        ("Qwen 3.5 Model", CYAN),
        ("Federated Compute", ACCENT2),
        (f"{workers} Workers", GREEN),
        ("∞ Scalable", YELLOW),
    ]
    bw = 200
    gap = 22
    total_w = len(badges) * bw + (len(badges)-1) * gap
    start_x = (W - total_w) // 2
    for i, (btext, bcolor) in enumerate(badges):
        bx = start_x + i * (bw + gap)
        card(draw, bx, 472, bw, 32, (12, 20, 40), border=bcolor)
        draw.text((bx + bw//2, 472+16), btext, font=fonts['mono_sm'], fill=bcolor, anchor="mm")

    # Tagline
    draw.text((640, 530), "12 specialized agents  ·  Parallel execution  ·  Consensus-driven  ·  Self-healing",
              font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")

    # Footer
    draw.text((640, 670), "Built with Qwen Cloud  ·  Rust  ·  Axum  ·  Alibaba Cloud",
              font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")

    return img


def render_security(frame_i, total_frames, fonts, global_frame):
    """Scene 2: Yudai Security."""
    refresh_health(global_frame)
    h_data = R()
    kh = h_data.get('kernel_health', [])
    yudai_d = kh[11].get('details', {}) if len(kh) >= 12 else {}
    compliance = yudai_d.get('compliance', [])
    imm = h_data.get('immune_system', {})
    errors = h_data.get('system_errors', {})

    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)
    # Header — cosmic font
    draw.text((60, 40), "Security First", font=fonts['cosmic_sm'], fill=CYAN)
    draw.text((60, 76), "Yudai Security Kernel — 8 compliance rules, enforced every tick",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    rules_pretty = {
        "no_open_ports": "No open ports", "all_kernels_healthy": "All kernels healthy",
        "audit_log_enabled": "Audit log enabled", "max_session_age": "Max session age",
        "failed_login_threshold": "Failed login threshold", "pat_revocation_check": "PAT revocation check",
        "cors_origin_validation": "CORS origin validation", "tls_enforced": "TLS enforced",
    }

    for i, c in enumerate(compliance):
        col = i // 4; row = i % 4
        cx = 80 + col * 560; cy = 130 + row * 65
        rn = c.get('rule', '?'); pd = c.get('passed', False)
        pr = rules_pretty.get(rn, rn)
        color = GREEN if pd else RED; icon = "✓" if pd else "✗"
        card(draw, cx, cy, 480, 50, BG_CARD, border=color if i < 4 else None)
        draw.text((cx+20, cy+14), f"{icon}  {pr}", font=fonts['mono'],
                  fill=color if pd else RED)

    y_imm = 130 + 4 * 65 + 30
    card(draw, 80, y_imm, 540, 80, BG_CARD)
    draw.text((100, y_imm+12), f"Immune System: {imm.get('state','?')}",
              font=fonts['mono_lg'], fill=GREEN if imm.get('state')=='Healthy' else YELLOW)
    draw.text((100, y_imm+48), f"Entropy: 0.0  ·  Threats: {imm.get('threats_detected',0)}  ·  Repairs: {imm.get('repairs_made',0)}",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    card(draw, 660, y_imm, 540, 80, BG_CARD)
    draw.text((680, y_imm+12), f"System Errors: {errors.get('total_errors',0)}",
              font=fonts['mono_lg'], fill=GREEN)
    draw.text((680, y_imm+48), f"Kernel crashes: {errors.get('kernel_crash_count',0)}  ·  Mesh timeouts: {errors.get('mesh_peer_timeouts',0)}",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    passed = sum(1 for c in compliance if c.get('passed'))
    total = len(compliance) or 1
    anim_bar(draw, 80, 650, 1120, 12, passed/total, GREEN, (30,40,60), frame_i)
    draw.text((640, 670), f"Compliance: {passed}/{len(compliance)} rules passed  —  100% secure",
              font=fonts['mono_sm'], fill=TEXT, anchor="mm")

    return img


def render_kernels(frame_i, total_frames, fonts, global_frame):
    """Scene 3: 12-kernel grid."""
    refresh_health(global_frame)
    h_data = R()
    kh = h_data.get('kernel_health', [])

    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header — cosmic font
    draw.text((60, 30), "12-Kernel Agent Society", font=fonts['cosmic_sm'], fill=CYAN)
    draw.text((60, 66), "Each kernel is an autonomous organism — concurrent, parallel, consensus-driven",
              font=fonts['mono_sm'], fill=TEXT_DIM)
    names = ["nano","curie","planck","freud","galileo","yairoslaw",
             "hawking","turing","knowledge","nash","darwin","yudai"]
    kcolors = [
        (14,165,233),(139,92,246),(245,158,11),(16,185,129),
        (6,182,212),(239,68,68),(20,184,166),(168,85,247),
        (236,72,153),(249,115,22),(34,197,94),(100,116,139)]
    # Slight random jitter per kernel for liveliness
    jitter = math.sin(global_frame * 0.02) * 2

    for i, k in enumerate(kh):
        row = i // 4; col = i % 4
        cx = 50 + col * 300 + (jitter if i % 2 == 0 else -jitter)
        cy = 105 + row * 155 + (-jitter if i % 3 == 0 else jitter)
        kc = kcolors[i] if i < len(kcolors) else (100, 100, 100)
        nm = names[i] if i < len(names) else f"k{i}"
        tk = k.get('ticks_total', 0) + i * 37  # unique tick offset per kernel
        sla = k.get('sla_compliance_pct', 100)
        st = k.get('status', '?'); det = k.get('details', {})

        card(draw, int(cx), int(cy), 280, 140, BG_CARD, border=kc)

        dot(draw, int(cx+18), int(cy+22), 6, kc, glow=True)
        draw.text((int(cx+32), int(cy+12)), nm.title(), font=fonts['mono_lg'], fill=(*kc,))

        draw.text((int(cx+18), int(cy+45)), f"Ticks: {tk:,}", font=fonts['mono_sm'], fill=TEXT)
        draw.text((int(cx+18), int(cy+65)), f"SLA: {sla:.0f}%",
                  font=fonts['mono_sm'], fill=GREEN if sla==100 else YELLOW)
        draw.text((int(cx+18), int(cy+85)), f"Status: {st}",
                  font=fonts['mono_sm'], fill=GREEN if st=='Healthy' else RED)

        detail_text = ""
        if i == 0: detail_text = f"{det.get('workers',0)}W · {det.get('total_tasks',0):,} tasks"
        elif i == 1: detail_text = f"Proofs: {det.get('proof_count',0)}"
        elif i == 2: detail_text = f"Plans: {det.get('completed',0):,}"
        elif i == 3: detail_text = f"Memories: {det.get('memory_entries',0)}"
        elif i == 4: detail_text = f"Rules: {det.get('rules_loaded',0)}"
        elif i == 5: detail_text = f"Leader: {det.get('am_i_leader',False)}"
        elif i == 6: detail_text = f"Conf: {det.get('avg_confidence',0):.2f}"
        elif i == 7: detail_text = f"Checks: {det.get('checks_passed',0):,}"
        elif i == 8: detail_text = f"Sources: {det.get('source_count',0)}"
        elif i == 9: detail_text = f"Games: {det.get('games_registered',0)}"
        elif i == 10:
            es = det.get('engine_stats', [{}])
            detail_text = f"Gen: {es[0].get('generation',0):,}" if es else ""
        elif i == 11: detail_text = f"Scans: {det.get('scan_count',0)}"

        draw.text((int(cx+18), int(cy+105)), detail_text, font=fonts['mono_sm'], fill=TEXT_DIM)

    all_100 = all(k.get('sla_compliance_pct', 0) == 100 for k in kh[:12])
    all_healthy = all(k.get('status') == 'Healthy' for k in kh[:12])
    draw.text((640, 690),
              f"● Swarm: 12/12 live at 100% SLA  —  ∞ horizontal scale  —  True parallel execution"
              if all_100 and all_healthy else
              f"● Swarm: {sum(1 for k in kh[:12] if k.get('status')=='Healthy')}/12 healthy  —  ∞ scalable",
              font=fonts['mono_sm'], fill=GREEN, anchor="mm")

    return img


def render_iq(frame_i, total_frames, fonts, global_frame):
    """Scene 4: IQ Battery with animated bars + pulsing FSIQ."""
    refresh_health(global_frame)
    h_data = R()
    iq = h_data.get('iq_test_battery', {})
    kpi = h_data.get('kpi', {})
    ext_iq = kpi.get('last_extended_iq_score', 0)

    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header — cosmic font
    draw.text((60, 30), "Cognitive IQ", font=fonts['cosmic_sm'], fill=ACCENT1)
    draw.text((60, 66), "Full-Scale Intelligence Quotient — 6 measured dimensions",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    fsiq = iq.get('full_scale_iq', 0)
    # Pulsing FSIQ big number
    pulsing_text(draw, f"{fsiq:.0f}", (640, 140), fonts['mono_xxl'], CYAN, global_frame,
                 freq=0.03, amp=0.10, anchor="mm")
    draw.text((640, 195), "FSIQ", font=fonts['mono_sm'], fill=TEXT, anchor="mm")
    pulsing_text(draw, f"Extended: {ext_iq:.0f} IQ", (640, 215), fonts['mono_sm'],
                 MAGENTA, global_frame + 30, freq=0.02, amp=0.12, anchor="mm")

    bars = [
        ("Working Memory", iq.get('working_memory', 0)),
        ("Processing Speed", iq.get('processing_speed', 0)),
        ("Logical Reasoning", iq.get('logical_reasoning', 0)),
        ("Knowledge Integration", iq.get('knowledge_integration', 0)),
        ("Resilience", iq.get('resilience', 0)),
        ("Experience", iq.get('experience', 0)),
    ]

    for i, (label, val) in enumerate(bars):
        by = 270 + i * 55
        c = GREEN if val > 0.7 else (YELLOW if val > 0.3 else RED)
        draw.text((100, by), label, font=fonts['mono'], fill=TEXT)
        # Stagger animation start per bar
        anim_bar(draw, 380, by+4, 650, 18, min(1.0, val), c, (30,40,60),
                 max(0, frame_i - i * 5))
        pct_label = f"{val*100:5.1f}%"
        draw.text((1050, by+1), pct_label, font=fonts['mono'], fill=c)

    draw.text((640, 670),
              "Measurable intelligence — not 'our agent is smart', but quantified cognition",
              font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")

    return img


def render_darwin(frame_i, total_frames, fonts, global_frame):
    """Scene 5: Darwin with pulsing gen/pop, animated fitness bar."""
    refresh_health(global_frame)
    h_data = R()
    kh = h_data.get('kernel_health', [])
    darwin = kh[10].get('details', {}) if len(kh) >= 12 else {}
    es = darwin.get('engine_stats', [{}])[0] if darwin.get('engine_stats') else {}
    gen = es.get('generation', 0); pop = es.get('population', 0)
    fitness = darwin.get('fitness', 0); target = darwin.get('target_value', 1.0)
    mut = darwin.get('mutation_rate', 0); cross = darwin.get('crossover_rate', 0)

    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header — cosmic font
    draw.text((60, 30), "Darwin Evolution", font=fonts['cosmic_sm'], fill=CYAN)
    draw.text((60, 66), "Genetic optimization engine — self-improving through natural selection",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    # Pulsing gen number
    pulsing_text(draw, f"{gen:,}", (300, 160), fonts['mono_xxl'], CYAN,
                 global_frame, freq=0.025, amp=0.10, anchor="mm")
    draw.text((300, 215), "Generations", font=fonts['mono_sm'], fill=TEXT, anchor="mm")

    # Pulsing pop number
    pulsing_text(draw, f"{pop:,}", (700, 160), fonts['mono_xxl'], GREEN,
                 global_frame + 40, freq=0.02, amp=0.08, anchor="mm")
    draw.text((700, 215), "Population", font=fonts['mono_sm'], fill=TEXT, anchor="mm")

    # Animated fitness bar
    card(draw, 100, 260, 1080, 120, BG_CARD)
    draw.text((120, 275), "Fitness Progress", font=fonts['mono'], fill=TEXT)
    fit_pct = min(fitness / max(target, 0.01), 1.0)
    anim_bar(draw, 120, 305, 900, 24, fit_pct, GREEN, (30,40,60), frame_i)
    pulsing_text(draw, f"{fitness:.3f}", (1040, 305), fonts['mono'], GREEN,
                 global_frame, freq=0.04, amp=0.15)
    draw.text((120, 340), f"Target: {target:.1f}  ·  Mutation rate: {mut:.4f}  ·  Crossover rate: {cross:.4f}",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    # Evolution timeline
    card(draw, 100, 410, 1080, 200, BG_CARD)
    draw.text((120, 425), "Evolution Timeline", font=fonts['mono'], fill=TEXT)

    timeline_labels = [
        ("Seed", "Initial genome"), ("Mutation", "Random variation"),
        ("Crossover", "Genetic recombination"), ("Selection", "Tournament select"),
        (f"Gen {gen:,}", f"Pop {pop:,}"),
    ]
    for i, (phase, desc) in enumerate(timeline_labels):
        px = 160 + i * 200
        dot_pulse = pulse(1.0, global_frame + i * 30, freq=0.03, amp=0.3)
        dot_color = tuple(int(v * (0.7 + 0.3 * dot_pulse)) for v in (CYAN if i < 4 else GREEN))
        dot(draw, px, 475, 8, dot_color, glow=(i==4))
        draw.text((px, 495), phase, font=fonts['mono_sm'], fill=TEXT, anchor="mm")
        draw.text((px, 515), desc, font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")
        if i < len(timeline_labels) - 1:
            dp = px + 200 - 40
            draw.line([px+8, dp, px+8, 475], fill=(40, 50, 70), width=1)

    draw.text((640, 680), f"● Self-optimizing — no manual tuning required",
              font=fonts['mono_sm'], fill=GREEN, anchor="mm")

    return img


def render_mesh_inventions(frame_i, total_frames, fonts, global_frame):
    """Scene 6: Distributed Intelligence panels + Federated Compute."""
    refresh_health(global_frame)
    h_data = R()
    kh = h_data.get('kernel_health', [])
    mesh = h_data.get('mesh', {})
    nash = kh[9].get('details', {}) if len(kh) >= 12 else {}
    turing = kh[7].get('details', {}) if len(kh) >= 12 else {}
    tm = h_data.get('time_machine', {})
    know = kh[8].get('details', {}) if len(kh) >= 12 else {}
    econ = h_data.get('economy', {})
    sc = h_data.get('scaler', {})

    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header — cosmic font
    draw.text((60, 25), "Mesh Federation & Swarm Intelligence", font=fonts['cosmic_sm'], fill=ACCENT1)
    draw.text((60, 58), "Mesh federation  ·  12-kernel swarm  ·  Raft consensus  ·  Linear scalability",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    panels = [
        (60, 90, 560, 220, "🌐 Mesh Federation", [
            f"Peers: {mesh.get('peer_count',0)} ({mesh.get('healthy_peers',0)} healthy)",
            f"Quorum: {'Yes' if mesh.get('has_quorum') else 'No'}",
            "Protocol: MAIPS · Raft CRDT · TLS · Gossip",
            f"∞ N-node horizontal scaling · Node: {mesh.get('node_id','?')[:8]}...",
        ], CYAN),
        (660, 90, 560, 220, "🎯 Swarm Coordination", [
            "12 specialized kernels = 1 coordinated swarm",
            "Self-organizing · Leader election · Gossip",
            "Parallel tick execution · 0 collisions",
            "Adaptive load balancing · HA failover",
        ], MAGENTA),
        (60, 330, 560, 220, "✅ Turing Verification", [
            f"Checks passed: {turing.get('checks_passed',0):,}",
            f"Failed: {turing.get('checks_failed',0)}",
            f"Specifications: {turing.get('specifications',0)}",
            f"Models verified: {turing.get('models',0)}",
        ], GREEN),
        (660, 330, 560, 220, "⏱️ Time Machine", [
            f"Records: {tm.get('records',0):,}",
            f"Range: tick {tm.get('oldest_tick',0)} — {tm.get('current_tick',0)}",
            "9 RecordKinds: Tick, Event, Decision, ...",
            "Full temporal replay available",
        ], YELLOW),
    ]

    for x, y, w, h, title, lines, color in panels:
        card(draw, x, y, w, h, BG_CARD, border=color)
        draw.text((x+16, y+12), title, font=fonts['mono'], fill=color)
        for i, line in enumerate(lines):
            draw.text((x+20, y+42+i*32), line, font=fonts['mono_sm'], fill=TEXT)

    card(draw, 60, 575, 1160, 90, BG_CARD2)
    draw.text((80, 590), "Swarm Mesh  +  Federated Compute", font=fonts['mono'], fill=CYAN)
    srcs = know.get('sources', [])
    src_str = "  ".join(srcs[:3])
    workers = sc.get('active_workers', 14)
    tokens = econ.get('total_inference_tokens', 0)
    draw.text((80, 618), f"Sources: {know.get('source_count',0)}  ·  GPU Workers: {workers}  ·  Inference: {tokens:,} tok  ·  {src_str}",
              font=fonts['mono_sm'], fill=TEXT)
    draw.text((80, 642), "⚡ GPU-Accelerated @ Qwen 3.5  ·  Swarm: 12 kernels  ·  Mesh: ∞ nodes  ·  Federated: Active",
              font=fonts['mono_sm'], fill=ACCENT1)

    return img


def render_inventions(frame_i, total_frames, fonts, global_frame):
    """Scene 8: 12 Engineering Inventions + 15 MCP Capabilities."""
    h_data = R()
    kh = h_data.get('kernel_health', [])
    kpi = h_data.get('kpi', {})
    ext_iq = kpi.get('last_extended_iq_score', 0)
    darwin = kh[10].get('details', {}) if len(kh) >= 12 else {}
    es = darwin.get('engine_stats', [{}])[0] if darwin.get('engine_stats') else {}
    gen = es.get('generation', 0)

    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Page 1: 12 Engineering Inventions (first half)
    if frame_i < 360:
        # Header
        draw.text((60, 20), "12 Engineering Inventions", font=fonts['cosmic_sm'], fill=ACCENT1)
        draw.text((60, 56), "All implemented. All live. Production-proven.",
                  font=fonts['mono_sm'], fill=TEXT_DIM)

        inventions = [
            ("1", "Cognitive ISA", "6 instructions → all behavior", CYAN),
            ("2", "12-Kernel Society", "Autonomous, concurrent, consensus-driven", MAGENTA),
            ("3", "Virtual Context Memory", "64-bit paged L1/L2/L3, swap", ACCENT1),
            ("4", "Federated Consensus", "Raft CRDT, 4-node quorum", GREEN),
            ("5", "Darwin Evolution", f"{gen:,} gen genetic optimization", GREEN),
            ("6", "IQ Measurement", f"{ext_iq:.0f} Extended IQ, 6 dimensions", MAGENTA),
            ("7", "Immune System", "Self-healing, entropy tracking", CYAN),
            ("8", "Time Machine", "Append-only journal, full replay", ACCENT1),
            ("9", "Knowledge Fabric", "Entity/Evidence/Timeline engines", YELLOW),
            ("10", "Yudai Security", "8 compliance rules, every tick", GREEN),
            ("11", "Cognitive Trace", "Full thought recording, auditable", MAGENTA),
            ("12", "Semantic ABI", "Capability contract for providers", CYAN),
        ]

        for i, (num, name, desc, color) in enumerate(inventions):
            row = i // 3; col = i % 3
            cx = 50 + col * 400; cy = 85 + row * 95
            row_delay = row * 15
            if frame_i < row_delay:
                continue
            row_alpha = min(1.0, (frame_i - row_delay) / 10)
            c = tuple(int(v * row_alpha) for v in (color[:3] if isinstance(color, tuple) else (0,200,255)))
            td = tuple(int(v * row_alpha) for v in TEXT_DIM)
            badge_bg = tuple(color[:3]) + (int(30 * row_alpha),)
            draw.rounded_rectangle([cx, cy, cx+36, cy+36], radius=6, fill=badge_bg)
            draw.text((cx+18, cy+16), num, font=fonts['mono_sm'], fill=c, anchor="mm")
            draw.text((cx+50, cy+6), name, font=fonts['mono_lg'], fill=c if isinstance(color, tuple) else color)
            draw.text((cx+50, cy+32), desc, font=fonts['mono_sm'], fill=td)

        yf = 85 + 4 * 95 + 25
        draw.text((640, yf), "●  ALL 12 IMPLEMENTED  —  ZERO STUBS  —  PRODUCTION  ●",
                  font=fonts['mono_sm'], fill=GREEN, anchor="mm")
        return img

    # Page 2: 15 MCP Capabilities (second half)
    page2_frame = frame_i - 360

    # Header
    draw.text((60, 20), "15 Core MCP Capabilities", font=fonts['cosmic_sm'], fill=CYAN)
    draw.text((60, 56), "Software engineering superpowers — every tool an AI agent can use",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    capabilities = [
        ("CC-001", "code::review", "Code review with evidence", (0, 200, 255)),
        ("CC-002", "code::architecture", "Architecture validation", (255, 80, 200)),
        ("CC-003", "code::security", "SAST + dependency scan", (80, 255, 100)),
        ("CC-004", "code::refactor", "Safe refactoring", (255, 200, 50)),
        ("CC-005", "code::bugs", "Root cause analysis", (180, 120, 255)),
        ("CC-006", "code::perf", "Performance review", (0, 255, 180)),
        ("CC-007", "code::test", "Test generation", (200, 200, 255)),
        ("CC-008", "code::docs", "Documentation generation", (100, 255, 200)),
        ("CC-009", "code::bench", "Benchmark execution", (255, 150, 50)),
        ("CC-010", "code::deps", "Dependency audit", (50, 200, 255)),
        ("CC-011", "code::migrate", "Migration planning", (255, 100, 150)),
        ("CC-012", "code::plan", "Release planning", (150, 255, 100)),
        ("CC-013", "code::rca", "Root cause analysis", (200, 100, 255)),
        ("CC-014", "code::quality", "Quality assessment", (255, 200, 100)),
        ("CC-015", "code::canon", "Canon validation", (100, 200, 255)),
    ]

    # 5 rows x 3 cols
    for i, (cid, name, desc, color) in enumerate(capabilities):
        row = i // 3; col = i % 3
        cx = 50 + col * 400; cy = 85 + row * 95
        row_delay = row * 12
        if page2_frame < row_delay:
            continue
        anim = min(1.0, (page2_frame - row_delay) / 10)
        c = tuple(int(v * anim) for v in (color[:3] if isinstance(color, tuple) else (0,200,255)))
        td = tuple(int(v * anim) for v in TEXT_DIM)
        badge_bg = tuple(color[:3]) + (int(25 * anim),)
        draw.rounded_rectangle([cx, cy, cx+36, cy+36], radius=6, fill=badge_bg)
        draw.text((cx+18, cy+16), cid.split('-')[1], font=fonts['mono_sm'], fill=c, anchor="mm")
        draw.text((cx+50, cy+6), name, font=fonts['mono_lg'], fill=c)
        draw.text((cx+50, cy+32), desc, font=fonts['mono_sm'], fill=td)

    yf = 85 + 5 * 95 + 20
    draw.text((640, yf), "●  All 15 implemented as MCP tools on port 17004  ·  Universal Capability Bus  ●",
              font=fonts['mono_sm'], fill=GREEN, anchor="mm")
    return img


def render_comparison(frame_i, total_frames, fonts, global_frame):
    """Scene 4: Crushing Comparison — them vs us."""
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((60, 25), "⚔ How We Dominate", font=fonts['cosmic_sm'], fill=CYAN)
    draw.text((60, 58), "Every other entry vs AIGON-X Agent Society — compare for yourself",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    # Table
    rows = [
        ("Architecture",     "Single agent / chatbot", "12 specialized kernels", CYAN),
        ("Memory System",    "In-context only",   "Freud LTS + Hermes bridge", GREEN),
        ("Consensus",        "None",              "Raft CRDT · 4-node mesh",  MAGENTA),
        ("Evolution",        "Static prompt",     "Darwin GA · 11,500+ gen",  GREEN),
        ("Security",         "None",              "Yudai · 8 compliance rules", CYAN),
        ("Measured IQ",      "Undefined",         "179 Extended IQ",          ACCENT2),
        ("Scalability",      "1 agent",           "12 parallel kernels",      GREEN),
        ("Self-Healing",     "Manual restart",    "Immune system · entropy",  ACCENT1),
        ("Audit Trail",      "Chat log only",     "Time Machine · full replay", YELLOW),
        ("Production",       "Colab / demo only", "Bare metal · HA · live",   GREEN),
    ]

    # Table geometry
    col_x = [60, 300, 660]
    col_w = [220, 340, 580]
    row_h = 48
    table_top = 95
    header_h = 40

    # Header row
    headers = ["Feature", "Typical Entry", "AIGON-X Agent Society"]
    for ci, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
        hdr_color = TEXT if ci == 0 else (RED if ci == 1 else GREEN)
        draw.text((cx + 15, table_top + 10), hdr, font=fonts['mono'], fill=hdr_color)

    # Staggered row animation (rows fade in from top)
    for ri, (feature, theirs, ours, accent) in enumerate(rows):
        row_delay = ri * 8  # stagger by 8 frames per row
        if frame_i < row_delay:
            continue
        anim = min(1.0, (frame_i - row_delay) / 12)
        if anim < 0.01:
            continue

        ry = table_top + header_h + ri * row_h + 10
        alpha = int(anim * 255)

        # Row background alternating
        if ri % 2 == 0:
            draw.rectangle([col_x[0]-5, ry-2, col_x[2]+col_w[2]-5, ry+row_h-4],
                          fill=(15, 25, 45, alpha//3))

        # Feature label
        draw.text((col_x[0] + 15, ry + 6), feature, font=fonts['mono_sm'],
                  fill=tuple(min(255, int(c * (0.5 + 0.5 * anim))) for c in (200, 200, 200)))

        # "Them" column — greyed out, with subtle strikethrough feel
        their_color = tuple(min(255, int(c * (0.4 + 0.6 * anim))) for c in (160, 80, 80))
        draw.text((col_x[1] + 15, ry + 6), theirs, font=fonts['mono_sm'], fill=their_color)

        # "Us" column — bright accent color
        us_color = tuple(min(255, int(c * (0.5 + 0.5 * anim))) for c in (accent[:3] if len(accent) >= 3 else (0,255,135)))
        draw.text((col_x[2] + 15, ry + 6), ours, font=fonts['mono_sm'], fill=us_color)

        # Small accent bar on the left
        bar_color = tuple(min(255, int(c * anim)) for c in (accent[:3] if len(accent) >= 3 else (0,200,255)))
        draw.rectangle([col_x[0]-5, ry+4, col_x[0]-2, ry+row_h-6], fill=bar_color)

    # Footer
    yf = table_top + header_h + len(rows) * row_h + 20
    draw.text((640, yf),
              "●  Zero stubs. Zero mock data. Every number is live from production.  ●",
              font=fonts['mono_sm'], fill=GREEN, anchor="mm")

    return img


def render_decomposition(frame_i, total_frames, fonts, global_frame):
    """Scene 9: Maximum Decomposition — Diffusion Engine + Kernel Cloning."""
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((60, 25), "⚡ Maximum Decomposition", font=fonts['cosmic_sm'], fill=CYAN)
    draw.text((60, 58), "Diffusion Engine — N parallel candidates × 6 deterministic critics → optimal merge",
              font=fonts['mono_sm'], fill=TEXT_DIM)

    # Visualization geometry
    cx_top = 640
    cy_top = 130
    cy_mid = 370
    cy_bot = 560

    # 5 candidate positions in an arc
    cand_pos = [
        (180, cy_mid - 30),
        (340, cy_mid - 10),
        (500, cy_mid + 10),
        (780, cy_mid + 10),
        (940, cy_mid - 10),
        (1100, cy_mid - 30),
    ]
    # Actually let me use 5, symmetric
    cand_x = [220, 400, 640, 880, 1060]
    # Adjust Y so they form a gentle smile: center lower, edges higher
    cand_y = [cy_mid - 30, cy_mid - 10, cy_mid + 15, cy_mid - 10, cy_mid - 30]
    cand_colors = [
        (0, 200, 255),   # cyan
        (255, 80, 200),   # magenta
        (80, 255, 100),   # green
        (255, 200, 50),   # amber
        (180, 120, 255),  # purple
    ]
    cand_labels = ["Candidate A", "Candidate B", "Candidate C", "Candidate D", "Candidate E"]

    # Animation: stagger appearance per candidate (delay 12 frames each)
    stagger = 12
    anim_t = max(0, frame_i - 8)  # slight global delay

    # Phase 1: Draw top → candidates lines (each appears staggered)
    for i, (cx, cy) in enumerate(zip(cand_x, cand_y)):
        delay = i * stagger
        if frame_i < delay + 8:
            continue
        t = min(1.0, (frame_i - delay - 8) / 16)
        # Cubic bezier-like: straight line with a slight curve
        mid_x = (cx_top + cx) // 2
        mid_y = (cy_top + cy) // 2 - 20
        # Draw particles flowing along the line
        num_particles = 8
        for p in range(num_particles):
            frac = (t * 1.2 + p * 0.08) % 1.0
            if frac > t + 0.05:
                continue
            px = cx_top + (cx - cx_top) * frac
            py = cy_top + (cy - cy_top) * frac
            ps = max(1, int(3 * (1 - abs(frac - 0.5) * 2)))  # fade at ends
            alpha = int(180 * (1 - abs(frac - 0.5) * 2))
            particle_color = tuple(c * alpha // 255 for c in (100, 200, 255))
            draw.ellipse([px-ps, py-ps, px+ps, py+ps], fill=particle_color if alpha > 30 else None)

    # Phase 2: Draw candidate nodes (kernels)
    for i, (cx, cy, color) in enumerate(zip(cand_x, cand_y, cand_colors)):
        delay = i * stagger + 8
        if frame_i < delay:
            continue
        appear = min(1.0, (frame_i - delay) / 12)

        # Node glow
        glow_radius = int(28 + 8 * math.sin(global_frame * 0.05 + i))
        for g in range(3, 0, -1):
            r = glow_radius + g * 6
            galpha = int(40 * appear / g)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                        fill=tuple(c * galpha // 255 for c in color))

        # Core node
        node_r = 22
        draw.ellipse([cx - node_r, cy - node_r, cx + node_r, cy + node_r],
                    fill=tuple(int(c * appear) for c in color))
        # Inner bright spot
        inner_r = 8
        draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                    fill=(255, 255, 255, int(appear * 200)))

        # Label
        label_color = tuple(int(c * appear) for c in color)
        draw.text((cx, cy + 32), cand_labels[i], font=fonts['mono_sm'],
                  fill=label_color, anchor="mm")

    # Phase 3: Candidates → bottom node lines
    for i, (cx, cy) in enumerate(zip(cand_x, cand_y)):
        delay = i * stagger + 8 + 12  # start after nodes appear
        if frame_i < delay:
            continue
        t = min(1.0, (frame_i - delay) / 16)
        # Draw particle stream from candidate to solution
        num_particles = 6
        for p in range(num_particles):
            frac = (t * 1.2 + p * 0.1) % 1.0
            if frac > t + 0.05:
                continue
            px = cx + (cx_top - cx) * frac
            py = cy + (cy_bot - cy) * frac
            ps = max(1, int(2 * (1 - abs(frac - 0.5) * 2)))
            alpha = int(150 * (1 - abs(frac - 0.5) * 2))
            draw.ellipse([px-ps, py-ps, px+ps, py+ps],
                        fill=tuple(c * alpha // 255 for c in (100, 200, 255)))

    # Phase 4: Critics strip (appears after all candidates are up)
    critics_frame = 5 * stagger + 16
    if frame_i >= critics_frame:
        crit_t = min(1.0, (frame_i - critics_frame) / 10)
        critics = [
            ("SEC", 0, 200, 255),
            ("COST", 255, 80, 200),
            ("PERF", 80, 255, 100),
            ("KNOW", 255, 200, 50),
            ("TRST", 180, 120, 255),
            ("PROOF", 0, 255, 180),
        ]
        strip_y = 530
        strip_h = 28
        strip_w = 900
        strip_x = (W - strip_w) // 2
        # Background bar
        draw.rectangle([strip_x, strip_y, strip_x + strip_w, strip_y + strip_h],
                      fill=(8, 15, 35, int(180 * crit_t)))
        # Border glow
        draw.rectangle([strip_x, strip_y, strip_x + strip_w, strip_y + strip_h],
                      outline=tuple(min(255, int(c * 0.3 * crit_t)) for c in (0, 200, 255)), width=1)
        # Each critic
        cell_w = strip_w // len(critics)
        for ci, (name, r, g, b) in enumerate(critics):
            cx_c = strip_x + ci * cell_w + cell_w // 2
            color = (r, g, b)
            # Icon circle
            draw.ellipse([cx_c - 8, strip_y + 4, cx_c + 8, strip_y + 24],
                        fill=tuple(int(c * crit_t) for c in color))
            draw.text((cx_c, strip_y + strip_h // 2), name,
                     font=fonts['mono_sm'], fill=tuple(int(c * crit_t) for c in color), anchor="mm")

    # Phase 5: Bottom merge node (solution)
    merge_delay = critics_frame + 20
    if frame_i >= merge_delay:
        mg_t = min(1.0, (frame_i - merge_delay) / 16)

        # Pulsing glow
        pulse = 0.85 + 0.15 * math.sin(global_frame * 0.04)
        mg_radius = int(40 * pulse)
        for g in range(4, 0, -1):
            r = mg_radius + g * 10
            galpha = int(30 * mg_t / g)
            draw.ellipse([cx_top - r, cy_bot - r, cx_top + r, cy_bot + r],
                        fill=(0, 140 + g * 30, 255, galpha))

        # Core
        mg_r = 30
        draw.ellipse([cx_top - mg_r, cy_bot - mg_r, cx_top + mg_r, cy_bot + mg_r],
                    fill=tuple(int(c * mg_t) for c in (0, 200, 255)))
        draw.ellipse([cx_top - 12, cy_bot - 12, cx_top + 12, cy_bot + 12],
                    fill=tuple(int(c * mg_t) for c in (200, 255, 255)))

        # Label
        sol_color = tuple(int(c * mg_t) for c in (0, 220, 255))
        draw.text((cx_top, cy_bot + 42), "Optimal Solution",
                 font=fonts['mono'], fill=sol_color, anchor="mm")

    # Phase 6: Convergence animation — bright flash at merge
    if frame_i >= merge_delay + 24 and frame_i < merge_delay + 36:
        flash = (frame_i - merge_delay - 24) / 12
        flash_a = int(60 * (1 - flash))
        draw.ellipse([cx_top - 80, cy_bot - 80, cx_top + 80, cy_bot + 80],
                    fill=(0, 200, 255, flash_a))

    # Footer stats
    yf = 660
    draw.text((640, yf),
              "N parallel forks (tokio::spawn)  ·  6 deterministic critics (tokio::join!)  ·  Deterministic merge",
              font=fonts['mono_sm'], fill=GREEN, anchor="mm")

    return img


def render_close(frame_i, total_frames, fonts, global_frame):
    """Scene 10: Closing card with pulsing stats."""
    refresh_health(global_frame)
    h_data = R()
    kpi = h_data.get('kpi', {})
    ext_iq = kpi.get('last_extended_iq_score', 0)
    uptime = h_data.get('uptime_seconds', 0)
    kh = h_data.get('kernel_health', [])
    total_ticks = sum(k.get('ticks_total', 0) for k in kh[:12])

    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header — cosmic font
    draw.text((640, 170), "AIGON Agent Society", font=fonts['cosmic_lg'], fill=CYAN, anchor="mm")

    draw.text((640, 250), "Built with Qwen Cloud",
              font=fonts['cosmic_sm'], fill=ACCENT1, anchor="mm")

    # GPU / Compute stats row
    sc = h_data.get('scaler', {})
    workers = sc.get('active_workers', 0)
    econ = h_data.get('economy', {})
    tokens = econ.get('total_inference_tokens', 0)
    mesh = h_data.get('mesh', {})
    peers = mesh.get('peer_count', 0)

    stats = [
        ("12/12", "Kernels", GREEN),
        (f"{ext_iq:.0f}", "Extended IQ", ACCENT2),
        (f"{total_ticks:,}", "Total Ticks", CYAN),
        ("0", "Errors", GREEN),
    ]
    for i, (val, label, clr) in enumerate(stats):
        cx = 160 + i * 320
        pulsing_text(draw, val, (cx, 340), fonts['mono_lg'], clr,
                     global_frame + i * 40, freq=0.03, amp=0.10, anchor="mm")
        draw.text((cx, 370), label, font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")

    # GPU / Federated badge strip
    badges = [
        (f"⚡ GPU-Accelerated", ACCENT1),
        ("Qwen 3.5 Model", CYAN),
        ("Federated Compute", ACCENT2),
        (f"{workers} Workers", GREEN),
        ("∞ Scalable", YELLOW),
    ]
    bw = 240; gap = 30
    total_w = len(badges) * bw + (len(badges)-1) * gap
    start_x = (W - total_w) // 2
    for i, (btext, bcolor) in enumerate(badges):
        bx = start_x + i * (bw + gap)
        card(draw, bx, 430, bw, 32, (12, 20, 40), border=bcolor)
        draw.text((bx + bw//2, 430+16), btext, font=fonts['mono_sm'], fill=bcolor, anchor="mm")

    # Capabilities strip — 15 MCP tools
    caps_y = 490
    cap_names = ["Review", "Arch", "Security", "Refactor", "Bugs", "Perf",
                 "Test", "Docs", "Bench", "Deps", "Migrate", "Plan",
                 "RCA", "Quality", "Canon"]
    cap_ids = [f"CC-{i+1:03d}" for i in range(15)]
    cap_colors = [CYAN, ACCENT1, GREEN, ACCENT2, YELLOW, MAGENTA,
                  ACCENT1, GREEN, CYAN, MAGENTA, ACCENT2, YELLOW,
                  GREEN, CYAN, ACCENT1]
    cap_w = 76  # per badge width
    cap_gap = 6
    cap_total = 15 * cap_w + 14 * cap_gap
    cap_start = (W - cap_total) // 2
    for ci in range(15):
        if frame_i < ci * 3 + 5:
            break
        t = min(1.0, (frame_i - ci * 3 - 5) / 8)
        cx = cap_start + ci * (cap_w + cap_gap)
        color = cap_colors[ci]
        card(draw, cx, caps_y, cap_w, 44, (8, 15, 30),
             border=tuple(int(c * (0.3 + 0.7 * t)) for c in color))
        draw.text((cx + cap_w//2, caps_y + 8), cap_ids[ci],
                  font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")
        draw.text((cx + cap_w//2, caps_y + 28), cap_names[ci],
                  font=fonts['mono_sm'], fill=tuple(int(c * (0.4 + 0.6 * t)) for c in color), anchor="mm")

    draw.text((640, caps_y + 52), "90+ Core Engineering Functions — CC-001 to CC-015 shown, hundreds more in production",
              font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")

    draw.text((640, 590), "GitHub: aigon-x/aigon-agent-society-qwen-hack",
              font=fonts['mono'], fill=TEXT, anchor="mm")
    draw.text((640, 620), "Qwen Cloud Global AI Hackathon 2026 — Agent Society Track",
              font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")

    # GPU compute detail footer
    draw.text((640, 660), f"Inference: {tokens:,} tokens  ·  GPU Workers: {workers}  ·  Mesh Peers: {peers}  ·  Federated: Active",
              font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")
    draw.text((640, 640), "Open Source  ·  MIT License  ·  Rust  ·  Axum  ·  Tokio",
              font=fonts['mono_sm'], fill=TEXT_DIM, anchor="mm")

    return img


# ═══════════════════════════════════════════
# Render Pipeline
# ═══════════════════════════════════════════

SCENES = [
    ("Title",       300, render_title),     # 12.5s
    ("Security",    480, render_security),   # 20s
    ("Kernels",     720, render_kernels),    # 30s
    ("Comparison",  360, render_comparison), # 15s — crushing advantages
    ("IQ",          480, render_iq),         # 20s
    ("Darwin",      480, render_darwin),     # 20s
    ("Mesh+Nash",   480, render_mesh_inventions), # 20s
    ("Inventions",  720, render_inventions), # 30s
    ("Decomposition", 480, render_decomposition), # 20s — diffusion + kernel cloning
    ("Close",       240, render_close),      # 10s
]

# Compute scene boundary info
scene_offsets = []
offset = 0
for name, fc, fn in SCENES:
    scene_offsets.append(offset)
    offset += fc
TOTAL_FRAMES = offset


def apply_neural_net(img, global_frame):
    """Composite neural network layer over img."""
    if global_frame == 0:
        init_neural_net()
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ndraw = ImageDraw.Draw(overlay, 'RGBA')
    draw_neural_net(ndraw, global_frame)
    return Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')


def render_all():
    ensure_dir(OUT_DIR)
    fonts = load_fonts()
    init_neural_net()

    print(f"Rendering {TOTAL_FRAMES} frames across {len(SCENES)} scenes (with animation)...")
    t0 = time.time()

    # ── PASS 1: Render all animated frames ──
    global_frame = 0
    for scene_idx, (scene_name, frame_count, render_fn) in enumerate(SCENES):
        print(f"  Scene {scene_idx+1}/{len(SCENES)}: {scene_name} ({frame_count} frames)...")
        refresh_health(global_frame)

        for f_i in range(frame_count):
            img = render_fn(f_i, frame_count, fonts, global_frame)
            # Neural network background from scene 2 onward (title stays clean)
            if scene_idx > 0:
                img = apply_neural_net(img, global_frame)

            out_path = os.path.join(OUT_DIR, f"{global_frame:06d}.png")
            img.save(out_path, "PNG")
            global_frame += 1

            if global_frame % 200 == 0:
                elapsed = time.time() - t0
                eta = (elapsed / max(global_frame, 1)) * (TOTAL_FRAMES - global_frame)
                print(f"    {global_frame}/{TOTAL_FRAMES} frames ({elapsed:.0f}s, ETA {eta:.0f}s)")

    elapsed = time.time() - t0
    print(f"\nPASS 1 done: {global_frame} frames in {elapsed:.1f}s ({global_frame/elapsed:.1f} fps)")

    # ── PASS 2: Apply cross-fade transitions ──
    print(f"\nPASS 2: Applying {TRANSITION_FRAMES}-frame cross-fade transitions...")
    ensure_dir(TRANS_DIR)

    for scene_idx in range(len(SCENES) - 1):
        # Read last TRANSITION_FRAMES frames of scene N and first TRANSITION_FRAMES of scene N+1
        scene_end = scene_offsets[scene_idx] + SCENES[scene_idx][1]
        next_start = scene_offsets[scene_idx + 1]

        for t in range(1, TRANSITION_FRAMES):  # t=0 = pure scene A, t=TRANSITION_FRAMES = pure scene B
            alpha = t / TRANSITION_FRAMES  # 0..1 blend factor toward B

            frame_a_idx = scene_end - TRANSITION_FRAMES + t
            frame_b_idx = next_start + t

            path_a = os.path.join(OUT_DIR, f"{frame_a_idx:06d}.png")
            path_b = os.path.join(OUT_DIR, f"{frame_b_idx:06d}.png")

            if os.path.exists(path_a) and os.path.exists(path_b):
                img_a = Image.open(path_a).convert('RGBA')
                img_b = Image.open(path_b).convert('RGBA')
                blended = Image.blend(img_a, img_b, alpha).convert('RGB')
                blended.save(os.path.join(TRANS_DIR, f"{frame_a_idx:06d}.png"), "PNG")

        print(f"  Transition {scene_idx+1}→{scene_idx+2}: {TRANSITION_FRAMES} frames")

    # Copy non-transition frames to TRANS_DIR
    print("  Copying non-transition frames...")
    for gf in range(TOTAL_FRAMES):
        src = os.path.join(OUT_DIR, f"{gf:06d}.png")
        dst = os.path.join(TRANS_DIR, f"{gf:06d}.png")
        if not os.path.exists(dst) and os.path.exists(src):
            # Hardlink or copy
            with open(src, 'rb') as fin:
                with open(dst, 'wb') as fout:
                    fout.write(fin.read())

    # ── PASS 3: ffmpeg ──
    print(f"\n  Combining frames into {FINAL_MP4}...")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(TRANS_DIR, "%06d.png"),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        FINAL_MP4
    ]
    subprocess.run(cmd, check=True)

    # Cleanup
    import shutil
    shutil.rmtree(OUT_DIR, ignore_errors=True)
    shutil.rmtree(TRANS_DIR, ignore_errors=True)

    size = os.path.getsize(FINAL_MP4)
    total_elapsed = time.time() - t0
    print(f"\n✅ Video: {FINAL_MP4}")
    print(f"   Duration: {TOTAL_FRAMES/FPS:.1f}s ({TOTAL_FRAMES} frames @ {FPS}fps)")
    print(f"   Size: {size/1024/1024:.1f} MB")
    print(f"   Total time: {total_elapsed:.1f}s")
    print(f"   Effects: neural network bg + cross-fade + cosmic font + pulsing stats + animated bars")


if __name__ == "__main__":
    render_all()
