#!/usr/bin/env python3
"""Compose 3 final videos (EN, CN, PL) with audio + subtitles burned in."""
import subprocess, os

ASSETS = '/opt/aigon-x-new/products/qwen-hack/assets'
VID = 197.5

compositions = [
    ("demo-video-en.mp4", "narration_en.mp3", "subs_final.ass", "EN — Cornelius Sage", "eng"),
    ("demo-video-cn.mp4", "narration_cn.mp3", "subs_final.ass", "CN — Xiaoxiao", "zho"),
    ("demo-video-pl.mp4", "narration_pl.mp3", "subs_pl.ass", "PL — Piotr", "pol"),
]

for out_name, audio, subs, title, lang in compositions:
    out = f'{ASSETS}/{out_name}'
    print(f"=== {title} ===")
    cmd = [
        'ffmpeg', '-y',
        '-i', f'{ASSETS}/demo-video-v2.mp4',
        '-i', f'{ASSETS}/{audio}',
        '-i', f'{ASSETS}/{subs}',
        '-filter_complex',
        f"[0:v]subtitles={ASSETS}/{subs}:fontsdir=/usr/share/fonts[vout]; \
          [1:a]atrim=end={VID}[aout]",
        '-map', '[vout]', '-map', '[aout]',
        '-c:v', 'h264', '-b:v', '2M', '-maxrate', '2.5M', '-bufsize', '4M',
        '-c:a', 'aac', '-b:a', '128k',
        '-metadata', f'title=AIGON Agent Society — {title}',
        '-metadata', 'artist=Jakub Sniegocki',
        '-metadata:s:a:0', f'language={lang}',
        '-movflags', '+faststart',
        out,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode == 0:
        size_mb = os.path.getsize(out) / (1024*1024)
        print(f"  ✅ {out_name} ({size_mb:.0f} MB)")
    else:
        print(f"  ❌ FAILED: {result.stderr[-200:]}")

print("\n=== ALL 3 VERSIONS COMPLETE ===")
