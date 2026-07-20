#!/usr/bin/env python3
"""Generate Polish SRT for 10-scene video."""
import re

SCENES = [
    ("AIGON Agent Society — dwanaście wyspecjalizowanych jąder AI. Qwen Cloud, Alibaba Cloud, produkcyjna inteligencja rozproszona.", "PL"),
    ("Yudai Security: osiem reguł compliance, zero błędów, system immunologiczny zdrowy.", "PL"),
    ("Dwanaście jąder — Nano, Curie, Planck, Freud, Galileo, Yairoslaw, Hawking, Turing, Knowledge, Nash, Darwin, Yudai. Wszystkie na SLA 100%.", "PL"),
    ("Jak miażdżymy konkurencję — dziesięć wymiarów przewagi. 12 kernel vs 1 agent loop. Raft CRDT vs brak. Darwin vs brak. IQ 179 vs tylko gadanie.", "PL"),
    ("Maksymalna dekompozycja — silnik dyfuzji, N równoległych kandydatów, 6 krytyków, łączenie. Prawdziwe równoległe wykonanie przez tokio spawn.", "PL"),
    ("IQ Poznawcze — sześć wymiarów. IQ pełnej skali 186, rozszerzone IQ 179. Mierzalna inteligencja.", "PL"),
    ("Ewolucja Darwina — 11 500+ pokoleń, 150 000+ osobników. Sprawność 0.912. System sam się optymalizuje.", "PL"),
    ("Federacja mesh — 4 węzły, konsensus Raft CRDT, 12 jąder jako jeden rój. Turing: 11 600+ kontroli.", "PL"),
    ("12 wynalazków inżynieryjnych — od Cognitive ISA po semantyczne ABI. Zero atrap, wszystko w produkcji.", "PL"),
    ("AIGON Agent Society z Qwen Cloud. 12/12 kernel, IQ 179, 140 000+ ticków, zero błędów. GPU, Rust, Axum, Tokio. Otwarte źródło.", "PL"),
]

# Scene frame boundaries (cumulative)
FRAMES = [300, 480, 720, 360, 480, 480, 480, 480, 720, 240]
TOTAL = sum(FRAMES)
fps = 24

def fmt_time(f):
    t = f / fps
    h, r = divmod(int(t), 3600)
    m, s = divmod(r, 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

offset = 0
entries = []
for i, (text, lang) in enumerate(SCENES):
    start_f = offset + 5  # 5-frame delay
    end_f = offset + FRAMES[i] - 5
    if lang == "PL":
        entries.append((start_f, end_f, f"[PL] {text}"))
    else:
        entries.append((start_f, end_f, text))
    offset += FRAMES[i]

lines = []
for idx, (sf, ef, text) in enumerate(entries, 1):
    lines.append(str(idx))
    lines.append(f"{fmt_time(sf)} --> {fmt_time(ef)}")
    lines.append(text)
    lines.append("")

srt = "\n".join(lines)
with open('/opt/aigon-x-new/products/qwen-hack/assets/subtitles_pl.srt', 'w', encoding='utf-8') as f:
    f.write(srt)
print(f"✅ SRT PL: 10 entries, {TOTAL}f ({TOTAL/24:.1f}s)")

# Generate ASS from bilingual SRT
def srt_to_ass_bilingual(srt_path, ass_path, en_entries, cn_entries, pl_entries):
    """
    Convert SRT entries to ASS format with bilingual styling.
    EN: top line (white), CN: bottom line (grey), PL: bottom line when PL-only
    """
    ass_lines = [
        "[Script Info]",
        "Title: AIGON Agent Society Bilingual Subtitles",
        "ScriptType: v4.00+",
        "PlayResX: 1280",
        "PlayResY: 720",
        "WrapStyle: 0",
        "",
        "[V4+ Styles]",
        "; EN style",
        "Style: EN,Arial,16,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,1,2,10,10,10,1",
        "; CN style (smaller, grey below EN)",
        "Style: CN,Noto Serif CJK SC,14,&H00CCCCCC,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,1,2,10,25,10,1",
        "; PL style",
        "Style: PL,Arial,16,&H00AADDFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,1,2,10,10,10,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    def to_ass_time(t):
        h, r = divmod(t, 3600000)
        m, ms = divmod(r, 60000)
        s, ms2 = divmod(ms, 1000)
        cs = ms2 // 10
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    # Parse SRT entries
    srt_items = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = content.strip().split('\n\n')
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            start_end = lines[1].split(' --> ')
            start_parts = list(map(int, start_end[0].replace(',', ':').split(':')))
            end_parts = list(map(int, start_end[1].replace(',', ':').split(':')))
            start_ms = start_parts[0]*3600000 + start_parts[1]*60000 + start_parts[2]*1000 + start_parts[3]
            end_ms = end_parts[0]*3600000 + end_parts[1]*60000 + end_parts[2]*1000 + end_parts[3]
            text = '\n'.join(lines[2:])
            srt_items.append((start_ms, end_ms, text))

    for idx, (sf, ef, text) in enumerate(srt_items):
        if idx < len(en_entries):
            style = "EN"
        elif idx < len(en_entries) + len(cn_entries):
            style = "CN"
        else:
            style = "PL"
        ass_line = f"Dialogue: 0,{to_ass_time(sf)},{to_ass_time(ef)},{style},,0,0,0,,{text}"
        ass_lines.append(ass_line)

    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ass_lines))
    print(f"✅ ASS PL: {len(srt_items)} entries -> {ass_path}")

# Create bilingual PL subs (same frame timing as SRT)
pl_bilingual = []
offset = 0
offset2 = 0
for i, (text, lang) in enumerate(SCENES):
    sf = offset + 5
    ef = offset + FRAMES[i] - 5
    if lang == "PL":
        pl_bilingual.append((sf, ef, text))
    offset += FRAMES[i]

srt_to_ass_bilingual(
    f'{"/opt/aigon-x-new/products/qwen-hack/assets/subtitles_pl.srt"}',
    f'{"/opt/aigon-x-new/products/qwen-hack/assets/subs_pl.ass"}',
    en_entries=pl_bilingual,
    cn_entries=[],
    pl_entries=[],
)

# Also create trilingual SRT (EN + CN + PL) for the PL video version
# For the PL version, show PL as primary, EN/CN as secondary
print("Done. Subtitles ready for Polish version.")
