"""
MM-EPC Real Image Validation
=============================
Addresses the #1 reviewer criticism: replaces text-proxied visual tasks
with real images. GPT-4o-mini Vision evaluates responses using actual images.
N=5 reps, 30 rounds, DeepSeek executor.
"""
import json, os, re, random, time, sys, urllib.request
from copy import deepcopy

# Keys
DS_KEY = ""
API2D_KEY = "fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7"
for p in [os.path.expanduser("~/AppData/Local/hermes/.env"), os.path.expanduser("~/.hermes/.env")]:
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'DEEPSEEK_API_KEY=(.+)', line)
                if m: DS_KEY = m.group(1).strip().strip('"').strip("'")
        if DS_KEY: break
    except: pass

STRATEGIES = {
    "step_by_step": "逐步推理", "critical_check": "先答再审", "first_principles": "基本原理",
    "creative_leap": "创新方案", "analogy_meta": "类比举例", "evidence_cite": "引用依据",
    "synthesis": "综合视角", "counterfactual": "反例边界",
    "visual_grounding": "先构建视觉画面再推理", "spatial_decompose": "空间/几何组件分解",
    "aesthetic_frame": "美学框架系统评估",
}

# Same text tasks
TEXT_TASKS = [
    {"mod": "text", "q": "1+2*3=?"}, {"mod": "text", "q": "5//2=?"},
    {"mod": "text", "q": "git撤销commit保留修改?"}, {"mod": "text", "q": "写回文判断函数。"},
    {"mod": "text", "q": "8硬币1假最少称?"}, {"mod": "text", "q": "设计短链接系统。"},
    {"mod": "text", "q": "索引为何用B+树?"}, {"mod": "text", "q": "Transformer并行优于LSTM?"},
]

# Visual tasks with REAL images (public URLs from Wikipedia, Unsplash, etc.)
VISUAL_TASKS_REAL = [
    {"mod": "visual", "q": "描述这张城市日落照片的色彩、构图和氛围。是否成功传达了平静与美丽的感觉？",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Sunset_2007-1.jpg/512px-Sunset_2007-1.jpg"},
    {"mod": "visual", "q": "这个立方体从45度角观察时能看到几个面？解释原因。",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Necker_cube.svg/256px-Necker_cube.svg.png"},
    {"mod": "visual", "q": "根据这张铁轨透视照片，解释为什么远处的物体看起来更小。",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Railroad_tracks_through_Larkspur_CA.jpg/512px-Railroad_tracks_through_Larkspur_CA.jpg"},
    {"mod": "visual", "q": "描述这张UML类图的结构、类和它们之间的关系。",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Uml_diagram.svg/512px-Uml_diagram.svg.png"},
    {"mod": "visual", "q": "评价这张照片的四个标准：构图、光线、色彩和主题。每项打分并说明理由。",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Mountain_landscape_at_sunset.jpg/512px-Mountain_landscape_at_sunset.jpg"},
    {"mod": "visual", "q": "分析这张照片中的三分法则构图。为什么这种构图方式有效？",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Rule_of_thirds_photo.jpg/512px-Rule_of_thirds_photo.jpg"},
    {"mod": "visual", "q": "识别这张图片中的互补色和类似色，分别举例说明它们在设计中的应用场景。",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Colorwheel.svg/512px-Colorwheel.svg.png"},
    {"mod": "visual", "q": "分析这张照片的色调（暖色调 vs 冷色调），描述它们各自传达的心理感受。",
     "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Ice_and_fire.jpg/512px-Ice_and_fire.jpg"},
]

def ds_gen(sp, up, temp=0.7, mt=400):
    body = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":temp}).encode()
    req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Authorization", f"Bearer {DS_KEY}")
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())["choices"][0]["message"]["content"]

def vision_eval(task, ans_a, ans_b, strat_a, img_url):
    """GPT-4o-mini Vision: evaluates using the real image."""
    up = [
        {"type": "text", "text": f"Evaluate which response is better for the given task.\nTask: {task}\n\nA ({strat_a}): {ans_a[:300]}\n\nB (step_by_step): {ans_b[:300]}\n\nOutput only A or B."},
        {"type": "image_url", "image_url": {"url": img_url}}
    ]
    body = json.dumps({"model":"gpt-4o-mini","messages":[{"role":"user","content":up}],"max_tokens":5,"temperature":0}).encode()
    req = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=body, method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Authorization", f"Bearer {API2D_KEY}")
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    txt = resp["choices"][0]["message"]["content"].strip().upper()
    return "A" if "A" in txt else ("B" if "B" in txt else ("A" if txt.startswith("A") else "B"))

def train_phase(name, task_list, initial_weights, rounds, seed, is_visual_with_images=False):
    random.seed(seed)
    w = deepcopy(initial_weights)
    n_tasks = len(task_list)
    wins = 0
    for i in range(rounds):
        tk = task_list[i % n_tasks]
        rv = random.random() * sum(w.values()); cu = 0.0; st = "step_by_step"
        for k, v in w.items():
            cu += v
            if rv <= cu: st = k; break
        for attempt in range(3):
            try:
                o = ds_gen(f"你是专家。策略：{STRATEGIES[st]}", tk["q"])
                c = ds_gen("你是专家。策略：逐步推理。", tk["q"])
                if is_visual_with_images and "img" in tk:
                    wn = vision_eval(tk["q"], o, c, st, tk["img"])
                else:
                    # Text eval for text tasks (no image)
                    up = f"Evaluate. Task: {tk['q']}\nA ({st}): {o[:300]}\nB (step_by_step): {c[:300]}\nBetter? Output only A or B."
                    body = json.dumps({"model":"gpt-4o-mini","messages":[{"role":"user","content":up}],"max_tokens":5,"temperature":0}).encode()
                    req = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=body, method="POST")
                    req.add_header("Content-Type","application/json"); req.add_header("Authorization", f"Bearer {API2D_KEY}")
                    resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
                    txt = resp["choices"][0]["message"]["content"].strip().upper()
                    wn = "A" if "A" in txt else ("B" if "B" in txt else ("A" if txt.startswith("A") else "B"))
                if wn == "A": wins += 1
                upd = 0.08 if wn == "A" else -0.04
                w[st] = max(0.001, w[st] + upd)
                tot = max(0.01, sum(w.values()))
                w = {k: max(0.001, v/tot) for k, v in w.items()}
                tot = sum(w.values()); w = {k: v/tot for k, v in w.items()}
                time.sleep(0.3)
                break
            except Exception as e:
                if attempt < 2: time.sleep(2**attempt)
                else: print(f"  [{name}] r{i} FAIL: {e}", flush=True)
    top_s = max(w, key=w.get)
    print(f"  [{name}] top={top_s}({w[top_s]:.0%}) wins={wins}/{rounds}", flush=True)
    return w

def contagion(w_pure, w_contaminated):
    pv = list(w_pure.values()); cv = list(w_contaminated.values())
    diff = sum((a-b)**2 for a,b in zip(pv,cv))**0.5
    norm = sum(v**2 for v in pv)**0.5
    return round(diff/max(0.001,norm), 4)

N = 10; R = 30
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiments")
os.makedirs(OUT, exist_ok=True)
CP = os.path.join(OUT, "real_image_checkpoint.json")
RES = os.path.join(OUT, "mm_epc_real_image.json")

results = []; start = 1
if os.path.exists(CP):
    with open(CP) as f:
        ck = json.load(f); results = ck.get("results",[]); start = len(results)+1
    print(f"Resumed from {len(results)}/{N}")

print(f"\nReal Image Validation: N={N}, R={R}")
t0 = time.time()
init = {k: 1/len(STRATEGIES) for k in STRATEGIES}

for rep in range(start, N+1):
    sb = rep*10000+R
    print(f"\n--- Rep {rep}/{N} ---", flush=True)
    try:
        w_T = train_phase("T", TEXT_TASKS, init, R, sb+1, False)
        w_V = train_phase("V-img", VISUAL_TASKS_REAL, init, R, sb+2, True)
        w_TV = train_phase("TV-img", VISUAL_TASKS_REAL, w_T, R, sb+3, True)
        w_VT = train_phase("VT", TEXT_TASKS, w_V, R, sb+4, False)
        gTV = contagion(w_V, w_TV); gVT = contagion(w_T, w_VT)
        asym = round(abs(gTV-gVT)/max(0.001,gTV+gVT),4)
        direction = "T->V" if gTV > gVT else ("V->T" if gVT > gTV else "symmetric")
        r = {"rep":rep,"gTV":gTV,"gVT":gVT,"asym":asym,"dir":direction,
             "top_T":max(w_T,key=w_T.get),"top_V":max(w_V,key=w_V.get),
             "top_TV":max(w_TV,key=w_TV.get),"top_VT":max(w_VT,key=w_VT.get),
             "time":time.time()-t0}
        results.append(r)
        print(f"  gTV={gTV:.3f} gVT={gVT:.3f} dir={direction}", flush=True)
        with open(CP,"w") as f: json.dump({"results":results,"last":rep},f,indent=2)
    except Exception as e:
        print(f"ERROR: {e}"); import traceback; traceback.print_exc()
        with open(CP,"w") as f: json.dump({"results":results,"last":rep-1,"error":str(e)},f,indent=2)
        sys.exit(1)

# Stats
gtv = [r["gTV"] for r in results]; gvt = [r["gVT"] for r in results]
diffs = [r["gVT"]-r["gTV"] for r in results]
m_tv = sum(gtv)/N; m_vt = sum(gvt)/N; m_d = sum(diffs)/N
sd_d = (sum((d-m_d)**2 for d in diffs)/(N-1))**0.5; se_d = sd_d/(N**0.5)
ci_lo = m_d-1.96*se_d; ci_hi = m_d+1.96*se_d
random.seed(42); bs = [sum([diffs[random.randint(0,N-1)] for _ in range(N)])/N for _ in range(10000)]
p2 = sum(1 for d in bs if abs(d)>=abs(m_d))/10000
v2t = sum(1 for r in results if r["gVT"]>r["gTV"])
t2v = sum(1 for r in results if r["gTV"]>r["gVT"])
z = sum(1 for r in results if r["gTV"]==0 and r["gVT"]==0)

final = {"experiment":"Real Image Validation","N":N,"R":R,
         "gTV_mean":round(m_tv,4),"gVT_mean":round(m_vt,4),"diff":round(m_d,4),
         "se":round(se_d,4),"ci95":[round(ci_lo,4),round(ci_hi,4)],
         "p":round(p2,4),"V->T":v2t,"T->V":t2v,"zeros":z,
         "results":results,"time":time.time()-t0}
with open(RES,"w") as f: json.dump(final,f,indent=2,ensure_ascii=False)

print(f"\n=== REAL IMAGE N={N} ===")
print(f"gTV={m_tv:.4f} gVT={m_vt:.4f} diff={m_d:.4f}+/-{se_d:.4f}")
print(f"95%CI:[{ci_lo:.4f},{ci_hi:.4f}] p={p2:.4f}")
print(f"V->T:{v2t} T->V:{t2v} zeros:{z}")
print(f"Saved: {RES}")
