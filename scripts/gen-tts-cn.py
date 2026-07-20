#!/usr/bin/env python3
"""Generate CN TTS via ElevenLabs Cornelius Sage."""
import subprocess, sys, os

KEY_PATH = '/opt/aigon-x/.claude/worktrees/agent-a9276fa15ef8545ab/vault/keys/elevenlabs-api.key'
os.environ['ELEVENLABS_API_KEY'] = open(KEY_PATH).read().strip()

from elevenlabs.client import ElevenLabs
client = ElevenLabs()

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

ASSETS = '/opt/aigon-x-new/products/qwen-hack/assets'

print('Generating CN ElevenLabs...')
for i, text in enumerate(CN_SCRIPT):
    result = client.text_to_speech.convert(voice_id='6sFKzaJr574YWVu4UuJF', text=text, output_format='mp3_44100_128')
    path = f'{ASSETS}/segments/cn_eleven_{i:02d}.mp3'
    with open(path, 'wb') as f:
        for chunk in result:
            if chunk: f.write(chunk)
    sz = __import__('os').path.getsize(path)
    print(f'  {i+1}/10: {sz}B')

# Concatenate
concat = f'{ASSETS}/segments/cn_concat.txt'
with open(concat, 'w') as f:
    for i in range(10):
        f.write(f"file '{ASSETS}/segments/cn_eleven_{i:02d}.mp3'\n")

out = f'{ASSETS}/narration_cn.mp3'
subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat, '-c', 'copy', out],
    capture_output=True, check=True)
dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
    '-of', 'default=noprint_wrappers=1:nokey=1', out], capture_output=True, text=True).stdout.strip()
print(f'\nOK narration_cn.mp3 ({float(dur):.1f}s)')
