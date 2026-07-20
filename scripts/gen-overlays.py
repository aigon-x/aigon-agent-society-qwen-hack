#!/usr/bin/env python3
"""
Generate competitive advantage overlays as transparent PNG frames
to be composited over the final video scenes.
"""
import os, math
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
ASSETS = '/opt/aigon-x-new/products/qwen-hack/assets'
OVERLAY_DIR = '/opt/aigon-x-new/products/qwen-hack/.overlays'
BG = (10, 14, 26)
GREEN = (0, 255, 135)
RED = (255, 70, 70)
CYAN = (0, 200, 255)
YELLOW = (255, 213, 0)

os.makedirs(OVERLAY_DIR, exist_ok=True)

# Fonts
try:
    mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    mono_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
    mono_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22)
    mono_xl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 28)
    cosmic = ImageFont.truetype("/usr/share/fonts/truetype/space-grotesk/SpaceGrotesk-Bold.ttf", 36)
    cosmic_sm = ImageFont.truetype("/usr/share/fonts/truetype/space-grotesk/SpaceGrotesk-Bold.ttf", 24)
except:
    mono = ImageFont.load_default()
    mono_sm = ImageFont.load_default()
    mono_lg = ImageFont.load_default()
    mono_xl = ImageFont.load_default()
    cosmic = ImageFont.load_default()
    cosmic_sm = ImageFont.load_default()

def card(draw, x, y, w, h, fill=(15, 23, 42, 220), border=None):
    """Rounded rect with alpha."""
    draw.rounded_rectangle([x, y, x+w, y+h], radius=6, fill=fill)
    if border:
        draw.rounded_rectangle([x, y, x+w, y+h], radius=6, outline=border, width=1)

def make_overlay(texts, frame_count, filename_prefix):
    """Generate frames for a comparison overlay that fades in and out."""
    for f_idx in range(frame_count):
        # Fade in 0→1 over 12 frames, hold, fade out last 12
        if f_idx < 12:
            alpha = f_idx / 12
        elif f_idx > frame_count - 12:
            alpha = (frame_count - f_idx) / 12
        else:
            alpha = 1.0
        
        if alpha < 0.01:
            continue
        
        overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Semi-transparent dark backdrop
        draw.rectangle([0, 0, W, H], fill=(0, 0, 0, int(120 * alpha)))
        
        # Comparison table card
        cx, cy, cw, ch = 140, 120, 1000, 480
        card(draw, cx, cy, cw, ch, fill=(10, 14, 26, int(230 * alpha)), border=CYAN)
        
        # Title
        draw.text((cx+30, cy+20), "⚔ Crushing Advantage", font=cosmic, fill=CYAN)
        
        # Comparison header row
        draw.text((cx+30, cy+75), "Feature", font=mono_lg, fill=YELLOW)
        draw.text((cx+350, cy+75), "Them (Typical Entry)", font=mono_lg, fill=(150, 150, 150))
        draw.text((cx+650, cy+75), "AIGON-X (Us)", font=mono_lg, fill=GREEN)
        draw.line([cx+20, cy+100, cx+cw-20, cy+100], fill=(40, 55, 80))
        
        # Table rows
        for i, (feature, them, us) in enumerate(texts):
            row_y = cy + 115 + i * 42
            draw.text((cx+30, row_y), feature, font=mono_sm, fill=(200, 200, 200))
            draw.text((cx+350, row_y), them, font=mono_sm, fill=(180, 100, 100))
            draw.text((cx+650, row_y), us, font=mono_sm, fill=GREEN)
        
        # Footer on overlay
        draw.text((cx+30, cy+ch-35), "Other entries: single agent loop. AIGON-X: 12-kernel society with consensus, evolution, memory, security.", 
                  font=mono_sm, fill=CYAN)
        
        out_path = os.path.join(OVERLAY_DIR, f"{filename_prefix}_{f_idx:04d}.png")
        overlay.save(out_path, "PNG")

# Scene 3 overlay (Kernels scene — during 12-kernel grid display)
# Show at 40% into the scene for 40% of it
SCENE3_FRAMES = 720
make_overlay([
    ("Architecture", "Single agent loop", "12 specialized kernels"),
    ("Memory", "In-context only", "Freud LTS + Hermes bridge"),
    ("Consensus", "None", "Raft CRDT via 4-node mesh"),
    ("Evolution", "Static prompt", "Darwin GA (11,500+ gen)"),
    ("Security", "None", "Yudai 8-rule scanner"),
    ("Measured IQ", "Undefined", "179 Extended IQ"),
], 240, "adv_scene3")

# Scene 8 overlay (Close scene — final comparison)
SCENE8_FRAMES = 240
make_overlay([
    ("Scalability", "1 agent / 1 thread", "12 kernels × parallel tick"),
    ("Self-healing", "Manual restart", "Immune system + drift"),
    ("LLM Integration", "Basic API call", "Qwen 3.5 + wq-plus + VL"),
    ("Federation", "None", "4-node mesh, MAIPS protocol"),
    ("Audit Trail", "Prompts only", "Time Machine, full replay"),
    ("Inventions", "0 (it's a demo)", "12 engineering inventions"),
], 180, "adv_scene8")

print(f"✅ Overlays generated in {OVERLAY_DIR}")
print(f"   Scene 3 overlay: 240 frames at 40% into Kernels (frames ~290-530)")
print(f"   Scene 8 overlay: 180 frames at start of Close")
