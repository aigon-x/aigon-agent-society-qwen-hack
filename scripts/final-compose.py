#!/usr/bin/env python3
"""Final composition: video + bilingual audio + Chinese subtitles.
Run AFTER render-video.py and gen-tts.py complete.
"""
import subprocess, os, sys

ASSETS = '/opt/aigon-x-new/products/qwen-hack/assets'
VIDEO = f'{ASSETS}/demo-video-v2.mp4'
SUBS_ASS = f'{ASSETS}/subs_final.ass'
EN_AUDIO = f'{ASSETS}/narration_en.mp3'
CN_AUDIO = f'{ASSETS}/narration_cn.mp3'
OUTPUT = f'{ASSETS}/demo-video-final.mp4'

# Validate inputs
missing = []
for path, label in [(VIDEO, 'Video'), (SUBS_ASS, 'ASS subs'), (EN_AUDIO, 'EN audio'), (CN_AUDIO, 'CN audio')]:
    if not os.path.exists(path):
        missing.append(label)
    
if missing:
    print(f"❌ Missing: {', '.join(missing)}")
    # Check sizes of what we do have
    for p, l in [(VIDEO, 'Video'), (EN_AUDIO, 'EN audio'), (CN_AUDIO, 'CN audio')]:
        if os.path.exists(p):
            sz = os.path.getsize(p) / (1024*1024)
            print(f"   {l}: {sz:.1f} MB")
    sys.exit(1)

# Get video duration
r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                    '-of', 'json', VIDEO], capture_output=True, text=True)
import json
vid_dur = float(json.loads(r.stdout)['format']['duration'])
print(f"Video: {vid_dur:.1f}s")

# Get audio durations
def audio_dur(path):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'json', path], capture_output=True, text=True)
    return float(json.loads(r.stdout)['format']['duration'])

en_dur = audio_dur(EN_AUDIO)
cn_dur = audio_dur(CN_AUDIO)
print(f"EN audio: {en_dur:.1f}s")
print(f"CN audio: {cn_dur:.1f}s")

# Build ffmpeg command
# Strategy: EN as main audio, CN as second audio track, bilingual ASS subtitles
cmd = [
    'ffmpeg', '-y',
    '-i', VIDEO,         # 0: video
    '-i', EN_AUDIO,      # 1: EN audio
    '-i', CN_AUDIO,      # 2: CN audio
    '-i', SUBS_ASS,      # 3: ASS subtitles

    '-map', '0:v:0',     # video stream
    '-map', '1:a:0',     # EN audio as main
    '-map', '2:a:0',     # CN audio as secondary

    # Video codec (re-encode to burn subtitles)
    '-vf', f"subtitles={SUBS_ASS}",
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
    '-pix_fmt', 'yuv420p',

    # Audio codecs
    '-c:a:0', 'aac', '-b:a:0', '128k', '-metadata:s:a:0', 'language=eng',
    '-c:a:1', 'aac', '-b:a:1', '128k', '-metadata:s:a:1', 'language=zho',

    # Metadata
    '-metadata', 'title=AIGON Agent Society — Qwen Cloud Global AI Hackathon 2026',
    '-metadata', 'artist=Jakub Sniegocki',
    '-metadata', 'comment=Built with Qwen Cloud. 12-kernel multi-agent cognitive runtime. Agent Society track.',

    OUTPUT
]

print(f"\nRunning ffmpeg... (output: {OUTPUT})")
result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

if result.returncode == 0:
    sz = os.path.getsize(OUTPUT) / (1024*1024)
    # Get final duration
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'json', OUTPUT], capture_output=True, text=True)
    final_dur = float(json.loads(r.stdout)['format']['duration'])
    print(f"\n✅ Final: {OUTPUT}")
    print(f"   Duration: {final_dur:.1f}s ({final_dur/60:.1f} min)")
    print(f"   Size: {sz:.1f} MB")
    print(f"   Audio: English (main) + Chinese (secondary)")
    print(f"   Subtitles: Bilingual (EN + CN)")
    print(f"   YouTube URL: file://{OUTPUT}")
else:
    print(f"❌ FFmpeg failed (code {result.returncode})")
    print(result.stderr[:800])
