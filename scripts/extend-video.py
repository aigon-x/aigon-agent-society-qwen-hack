#!/usr/bin/env python3
"""Extend render-video.py scene durations for longer voiceover."""
import re

with open('/opt/aigon-x-new/products/qwen-hack/scripts/render-video.py') as f:
    src = f.read()

# Double scene durations — simple multiplier
old_scenes = [
    ('"Title",       150', '"Title",       300'),       # 6.25s → 12.5s
    ('"Security",    240', '"Security",    480'),       # 10s → 20s
    ('"Kernels",     360', '"Kernels",     720'),       # 15s → 30s
    ('"IQ",          240', '"IQ",          480'),       # 10s → 20s
    ('"Darwin",      240', '"Darwin",      480'),       # 10s → 20s
    ('"Mesh+Nash",   240', '"Mesh+Nash",   480'),       # 10s → 20s
    ('"Inventions",  360', '"Inventions",  720'),       # 15s → 30s
    ('"Close",       120', '"Close",       240'),       # 5s → 10s
]

for old, new in old_scenes:
    assert old in src, f'Missing: {old}'
    src = src.replace(old, new)

with open('/opt/aigon-x-new/products/qwen-hack/scripts/render-video.py', 'w') as f:
    f.write(src)

print('Extended to 3840 frames = 160s @ 24fps')
