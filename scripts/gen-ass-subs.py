#!/usr/bin/env python3
"""Convert bilingual SRT to ASS with proper CNS font & layout."""
import re

SRT = '/opt/aigon-x-new/products/qwen-hack/assets/subtitles_bilingual.srt'
ASS_OUT = '/opt/aigon-x-new/products/qwen-hack/assets/subs_final.ass'

with open(SRT) as f:
    srt = f.read()

# Parse SRT
blocks = re.split(r'\n\s*\n', srt.strip())
entries = []
for block in blocks:
    lines = block.strip().split('\n')
    if len(lines) < 3:
        continue
    # idx = lines[0]
    time_line = lines[1]
    en_text = lines[2]
    cn_text = lines[3] if len(lines) > 3 else ''
    # Parse time
    m = re.match(r'(\d+:\d+:\d+,\d+)\s*-->\s*(\d+:\d+:\d+,\d+)', time_line)
    if m:
        entries.append((m.group(1), m.group(2), en_text, cn_text))

def to_ass_time(srt_time):
    h,m,s = srt_time.split(':')
    s_comma = s.replace(',', '.')
    return f"{h}:{m}:{s_comma}"

# Write ASS
lines = []
lines.append("[Script Info]")
lines.append("ScriptType: v4.00+")
lines.append("PlayResX: 1280")
lines.append("PlayResY: 720")
lines.append("ScaledBorderAndShadow: yes")
lines.append("")
lines.append("[V4+ Styles]")
lines.append("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding")
# Style for English: Space Grotesk, small, white
lines.append("Style: EN,Space Grotesk,14,&HCCFFFFFF,&H000000FF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.5,0.5,2,40,40,40,0")
# Style for Chinese: Noto Serif CJK SC, same size
lines.append("Style: CN,Noto Serif CJK SC,14,&HCCFFFFFF,&H000000FF,&H80000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.5,0.5,2,40,40,64,1")
lines.append("")

lines.append("[Events]")
lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")

for start, end, en, cn in entries:
    ass_start = to_ass_time(start)
    ass_end = to_ass_time(end)
    # First line: EN (style), Second line: CN (style) — use \N for new line
    # Put both in one event with mixed styles
    text = f"{{\\rEN}}{en}\\N{{\\rCN}}{cn}"
    lines.append(f"Dialogue: 0,{ass_start},{ass_end},EN,,0,0,0,,{text}")

with open(ASS_OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"✅ ASS subtitles: {ASS_OUT} ({len(entries)} entries)")
