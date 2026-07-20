#!/usr/bin/env python3
"""Generate English (ElevenLabs), Chinese (edge-tts), and Polish (ElevenLabs) TTS."""
import subprocess, os, sys, time

ASSETS = '/opt/aigon-x-new/products/qwen-hack/assets'

EN_SCRIPT = [
    "AIGON Agent Society — twelve specialized AI kernels working as one. Built with Qwen Cloud, deployed on Alibaba Cloud, powering production distributed intelligence.",
    "Security First. The Yudai Security Kernel enforces eight compliance rules every tick: no open ports, all kernels healthy, audit log enabled, TLS enforced. Zero system errors. The immune system is healthy — entropy zero, threats zero.",
    "Twelve kernels, each a specialist. Nano executes tasks, Curie reasons, Planck plans, Freud remembers. Galileo validates knowledge, Yairoslaw achieves consensus, Hawking manages confidence. Turing verifies, Knowledge connects sources, Nash plays strategic games, Darwin evolves through natural selection, and Yudai secures. All running in parallel at one hundred percent SLA.",
    "How we crush the competition. Ten dimensions: architecture, memory, consensus, evolution, security, measured IQ, scalability, self-healing, audit trail, and production readiness. Other entries use single agent loops and static prompts. We deliver twelve specialized kernels with Raft CRDT consensus, Darwin evolution, quantified IQ, and a live production system.",
    "Maximum Decomposition. The Diffusion Engine decomposes every problem into N parallel candidates, each running on a forked kernel via tokio spawn. Six deterministic critics evaluate security, cost, performance, knowledge, trust, and proof quality. The top candidates merge into an optimal solution. This is real parallel execution, not single threaded inference.",
    "Cognitive IQ — a quantified measurement of intelligence across six dimensions: working memory, processing speed, logical reasoning, knowledge integration, resilience, and experience. Full scale IQ one hundred eighty six, extended IQ one hundred seventy nine. Measurable intelligence, not just a claim.",
    "Darwin Evolution — a genetic optimization engine that self-improves through natural selection. Over eleven thousand five hundred generations, with a population of over one hundred fifty thousand individuals. Current fitness zero point nine one two. The system evolves continuously — no manual tuning required.",
    "Mesh Federation and Swarm Intelligence. Four-node mesh with Raft CRDT consensus, quorum active. Twelve kernels coordinated as a single swarm — self-organizing, leader-elected, zero collisions. Turing verification has passed over eleven thousand six hundred checks. The Time Machine records every tick for full temporal replay.",
    "Twelve engineering inventions, all implemented, all live in production. From cognitive instruction set architecture and twelve-kernel society, to virtual context memory, federated consensus, and Darwin evolution. IQ measurement, immune system, Time Machine, Knowledge Fabric, Yudai security, cognitive trace, and semantic ABI. Zero stubs, production proven.",
    "AIGON Agent Society — built with Qwen Cloud. Twelve of twelve kernels live, extended IQ one hundred seventy nine, over one hundred forty thousand total ticks, zero errors. GPU accelerated, Qwen three point five model, federated compute with fourteen workers, infinitely scalable. Open source, MIT license, Rust, Axum, Tokio. Visit the repository to learn more.",
]

CN_SCRIPT = [
    "AIGON Agent Society — 十二个专用AI内核协同工作。基于Qwen Cloud构建，部署在阿里云上，驱动生产级分布式智能。",
    "安全第一。Yudai安全内核在每个时钟周期执行八项合规规则。零系统错误。免疫系统健康。",
    "十二个内核各有所长。Nano执行，Curie推理，Planck规划，Freud记忆。Galileo验证，Yairoslaw共识，Hawking置信度管理。所有内核百分百SLA并行运行。",
    "我们如何碾压对手。十个维度全面领先：架构、内存、共识、进化、安全、IQ、可扩展性、自愈、审计和生产就绪。别人用单个Agent和静态提示，我们提供十二个专用内核、Raft CRDT共识、达尔文进化、量化IQ和实时生产系统。",
    "最大分解。扩散引擎将每个问题分解为N个并行候选方案，每个方案在fork后的内核上通过tokio spawn独立运行。六个确定性评审器评估安全性、成本、性能、知识、信任和证明质量。最优候选方案合并为最终结果。这是真正的并行执行，不是单线程推理。",
    "认知IQ — 六个维度的量化智能。全量表IQ 186，扩展IQ 179。可测量的智能，不是空口宣称。",
    "达尔文进化 — 通过自然选择的遗传优化。超过一万一千代，十五万个体。适应度0.912。持续自我优化，无需人工调参。",
    "网格联邦与群体智能。四节点Raft CRDT网格，十二内核群体协调，Turing验证通过万次检查，Time Machine完整时间回溯。GPU加速，Qwen模型，无限可扩展。",
    "十二项工程发明，全部实现，全部投产。从认知指令集到十二内核社会，联邦共识、达尔文进化、IQ测量、免疫系统、Yudai安全。零存根，生产验证。",
    "AIGON Agent Society 基于Qwen Cloud构建。十二内核全部在线，IQ 179，超十四万时钟周期，零错误。开源MIT许可，Rust Axum Tokio。访问代码仓库。",
]

PL_SCRIPT = [
    "AIGON Agent Society — dwanaście wyspecjalizowanych jąder AI pracujących jako jedno. Zbudowany na Qwen Cloud, wdrożony na Alibaba Cloud, napędzający produkcyjną inteligencję rozproszoną.",
    "Bezpieczeństwo przede wszystkim. Jądro Yudai egzekwuje osiem reguł zgodności każdego ticka. Zero błędów systemowych. System immunologiczny jest zdrowy — entropia zerowa, zagrożeń zero.",
    "Dwanaście wyspecjalizowanych jąder. Nano wykonuje zadania, Curie rozumuje, Planck planuje, Freud zapamiętuje. Galileo weryfikuje wiedzę, Yairoslaw osiąga konsensus, Hawking zarządza ufnością. Turing weryfikuje, Knowledge łączy źródła, Nash gra strategicznie, Darwin ewoluuje przez dobór naturalny, a Yudai chroni. Wszystkie działają równolegle przy stuprocentowej dostępności.",
    "Jak miażdżymy konkurencję. Dziesięć wymiarów: architektura, pamięć, konsensus, ewolucja, bezpieczeństwo, mierzalne IQ, skalowalność, samonaprawa, audyt i gotowość produkcyjna. Inni używają pojedynczej pętli agenta i statycznych promptów. My dostarczamy dwanaście wyspecjalizowanych jąder z konsensusem Raft CRDT, ewolucją darwinowską, kwantyfikowanym IQ i produkcyjnym systemem na żywo.",
    "Maksymalna dekompozycja. Silnik dyfuzji rozkłada każdy problem na N równoległych kandydatów, z których każdy działa na sklonowanym jądrze poprzez tokio spawn. Sześć deterministycznych krytyków ocenia bezpieczeństwo, koszt, wydajność, wiedzę, zaufanie i jakość dowodów. Najlepsi kandydaci łączą się w optymalne rozwiązanie. To prawdziwe równoległe wykonanie, a nie jednowątkowa inferencja.",
    "IQ Poznawcze — skwantyfikowany pomiar inteligencji w sześciu wymiarach: pamięć robocza, szybkość przetwarzania, logiczne wnioskowanie, integracja wiedzy, odporność i doświadczenie. IQ pełnej skali sto osiemdziesiąt sześć, rozszerzone IQ sto siedemdziesiąt dziewięć. Mierzalna inteligencja, a nie tylko deklaracja.",
    "Ewolucja Darwina — silnik optymalizacji genetycznej, który sam się ulepsza poprzez dobór naturalny. Ponad jedenaście i pół tysiąca pokoleń, z populacją ponad stu pięćdziesięciu tysięcy osobników. Sprawność: dziewięć setnych dwanaście. System ewoluuje w sposób ciągły — bez ręcznego strojenia.",
    "Federacja Mesh i Inteligencja Rojowa. Siatka czterech węzłów z konsensusem Raft CRDT, aktywne kworum. Dwanaście jąder koordynowanych jako jeden rój — samoorganizujący się, z wyborem lidera, zerową liczbą kolizji. Weryfikacja Turinga przeszła ponad jedenaście tysięcy sześćset kontroli. Wehikuł Czasu rejestruje każdy tick dla pełnego temporalnego odtworzenia.",
    "Dwanaście wynalazków inżynieryjnych, wszystkie zaimplementowane, wszystkie działające w produkcji. Od architektury poznawczego zestawu instrukcji i społeczeństwa dwunastu jąder, przez wirtualną pamięć kontekstu, federacyjny konsensus i ewolucję Darwina. Pomiar IQ, system immunologiczny, Wehikuł Czasu, Fabryka Wiedzy, bezpieczeństwo Yudai, ślad poznawczy i semantyczne ABI. Zero atrap, sprawdzone w produkcji.",
    "AIGON Agent Society — zbudowany z Qwen Cloud. Dwanaście z dwunastu jąder aktywnych, rozszerzone IQ sto siedemdziesiąt dziewięć, ponad sto czterdzieści tysięcy ticków, zero błędów. Przyspieszony GPU, model Qwen, obliczenia federacyjne z czternastoma workerami, nieskończenie skalowalny. Otwarte źródło, licencja MIT, Rust, Axum, Tokio. Odwiedź repozytorium, aby dowiedzieć się więcej.",
]

os.makedirs(f'{ASSETS}/segments', exist_ok=True)

def gen_elevenlabs(voice_id, text, out_path, timeout=120):
    """Generate TTS via ElevenLabs text_to_speech."""
    import os; os.environ["ELEVENLABS_API_KEY"] = "sk_51fd8833588a1612e0d646544aaf7129de723b1989f59f0e"
    from elevenlabs.client import ElevenLabs
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    try:
        result = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=text,
        )
        with open(out_path, 'wb') as f:
            for chunk in result:
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"  FAILED: {str(e)[:200]}")
        return False

def gen_edgetts(voice, text, out_path, timeout=120):
    """Generate TTS via edge-tts."""
    result = subprocess.run(
        ['python3', '-m', 'edge_tts', '--voice', voice,
         '--text', text, '--write-media', out_path],
        capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr[:200]}")
        return False
    return True

# ── English: ElevenLabs Cornelius Sage ──
print("=== English TTS (ElevenLabs Cornelius Sage) ===")
en_segments = []
for i, text in enumerate(EN_SCRIPT):
    out = f'{ASSETS}/segments/en_{i:02d}.mp3'
    print(f"  Scene {i+1}/10... ", end='', flush=True)
    if gen_elevenlabs('6sFKzaJr574YWVu4UuJF', text, out):
        en_segments.append(out)
        print("OK")

# ── Chinese: edge-tts ──
print("\n=== Chinese TTS (edge-tts) ===")
cn_segments = []
for i, text in enumerate(CN_SCRIPT):
    out = f'{ASSETS}/segments/cn_{i:02d}.mp3'
    print(f"  Scene {i+1}/10... ", end='', flush=True)
    if gen_edgetts('zh-CN-XiaoxiaoNeural', text, out):
        cn_segments.append(out)
        print("OK")

# ── Polish: ElevenLabs Piotr ──
print("\n=== Polish TTS (ElevenLabs Piotr) ===")
pl_segments = []
for i, text in enumerate(PL_SCRIPT):
    out = f'{ASSETS}/segments/pl_{i:02d}.mp3'
    print(f"  Scene {i+1}/10... ", end='', flush=True)
    if gen_elevenlabs('o2xdfKUpc1Bwq7RchZuW', text, out):
        pl_segments.append(out)
        print("OK")

# ── Concatenate ──
def concat_audio(segments, output, label):
    if not segments:
        print(f"  No {label} segments!")
        return
    list_path = f'{ASSETS}/segments/{label}_list.txt'
    with open(list_path, 'w') as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")
    result = subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', list_path, '-c', 'copy', output
    ], capture_output=True, text=True, timeout=120)
    if result.returncode == 0:
        sz = os.path.getsize(output) / 1024
        print(f"\n  ✅ {output} ({sz:.0f} KB)")
    else:
        print(f"\n  ❌ FFmpeg concat failed: {result.stderr[:200]}")

concat_audio(en_segments, f'{ASSETS}/narration_en.mp3', 'en')
concat_audio(cn_segments, f'{ASSETS}/narration_cn.mp3', 'cn')
concat_audio(pl_segments, f'{ASSETS}/narration_pl.mp3', 'pl')

print("\nDone! Check assets/narration_en.mp3, _cn.mp3, _pl.mp3")
