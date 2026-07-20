#!/usr/bin/env python3
import importlib.util, os, sys
work="/opt/aigon-x-new/products/qwen-hack/scripts"
src=open(f"{work}/render-video.py").read()
ok=0;fail=0
def c(l,cond):
    global ok,fail
    if cond: ok+=1; print(f"  PASS  {l}")
    else: fail+=1; print(f"  FAIL  {l}")

try: compile(src,"rv.py","exec"); c("compile",True)
except SyntaxError as e: print(f"SYNTAX ERROR: {e}"); sys.exit(1)

for feat in ["draw_neural_net","spawn_traveler","cosmic_lg","Scalable","Swarm","Qwen 3.5","ANIM_BAR_FRAMES = 48","born_at"]:
    c(feat, feat in src)

mod_src=src.replace("if __name__ == '__main__':","if False:")
mod=importlib.util.module_from_spec(spec:=importlib.util.spec_from_file_location("r",f"{work}/render-video.py"))
exec(compile(mod_src,"r.py","exec"),mod.__dict__)

mod.init_neural_net()
nd,cn,ad,tr=mod._nn_state
c("140 nodes", len(nd)==140)
c(">200 conns", len(cn)>200)
c("born_at frames", all(isinstance(c[3],int) for c in cn[:10]))

from PIL import Image, ImageDraw
for gf in range(0, 250, 25):
    mod.draw_neural_net(ImageDraw.Draw(Image.new('RGBA',(1280,720),(0,0,0,0)),'RGBA'),gf)
c("travelers active", len(tr)>0)

fonts=mod.load_fonts()
for n,fc,fn in mod.SCENES:
    try: img=fn(0,fc,fonts,0); c(f"scene {n}", img.size==(1280,720))
    except Exception as e: c(f"scene {n}");print(f"  ERR: {e}")

print(f"\n{ok}/{ok+fail} PASSED")
sys.exit(0 if fail==0 else 1)
