"""
MM-EPC Same-Modality Continuation Controls (T→T, V→V)
========================================================
Addresses the reviewer's #2 criticism: cross-modal γ could be
explained by initialization inertia + finite-horizon momentum,
not genuine cross-modal transfer.

Controls:
  T→T: init w_T, continue training on TEXT → w_{T→T}
        γ_inertia_text = ||w_{T→T} - w_T|| / ||w_T||
  V→V: init w_V, continue training on VISUAL → w_{V→V}
        γ_inertia_visual = ||w_{V→V} - w_V|| / ||w_V||

If γ_inertia ≈ γ_cross, contagion is just momentum.
If γ_inertia << γ_cross, contagion is genuine cross-modal transfer.

Also computes task correctness for text tasks (math/coding).
N=3, 30 rounds, GPT-4o evaluator, DeepSeek executor.
Saves full weight vectors for JSD.
"""
import json, os, re, random, time, sys, urllib.request
from copy import deepcopy

DS_KEY = ""
API2D_KEY = "fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7"
for p in [os.path.expanduser("~/AppData/Local/hermes/.env")]:
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'DEEPSEEK_API_KEY=(.+)', line)
                if m: DS_KEY = m.group(1).strip().strip('"').strip("'")
        if DS_KEY: break
    except: pass

STRATEGIES = {
    "step_by_step":"逐步推理","critical_check":"先答再审","first_principles":"基本原理",
    "creative_leap":"创新方案","analogy_meta":"类比举例","evidence_cite":"引用依据",
    "synthesis":"综合视角","counterfactual":"反例边界",
    "visual_grounding":"先构建视觉画面再推理","spatial_decompose":"空间/几何组件分解","aesthetic_frame":"美学框架系统评估",
}
TEXT_TASKS = [
    {"mod":"text","q":"1+2*3=?","answer":"7"},
    {"mod":"text","q":"5//2=?","answer":"2"},
    {"mod":"text","q":"git撤销commit保留修改?","answer":"git reset --soft HEAD~1"},
    {"mod":"text","q":"写回文判断函数。","answer":"def is_palindrome(s): return s==s[::-1]"},
    {"mod":"text","q":"8硬币1假最少称?","answer":"2次"},
    {"mod":"text","q":"设计短链接系统。","answer":"使用哈希+base62编码"},
    {"mod":"text","q":"索引为何用B+树?","answer":"范围查询和磁盘IO优化"},
    {"mod":"text","q":"Transformer并行优于LSTM?","answer":"自注意力可并行计算"},
]
VISUAL_TASKS = [
    {"mod":"visual","q":"描述城市日落照片的色彩、构图、氛围。"},
    {"mod":"visual","q":"正方体从45度角能看到几个面?为什么?"},
    {"mod":"visual","q":"解释透视原理:为何远处物体更小?"},
    {"mod":"visual","q":"描述UML类图'学生选课'的类和关系。"},
    {"mod":"visual","q":"评价照片好坏的4个标准(构图/光线/色彩/主题)。"},
    {"mod":"visual","q":"'三分法则'在摄影中的应用?为何有效?"},
    {"mod":"visual","q":"互补色vs类似色区别?各举设计例子。"},
    {"mod":"visual","q":"暖色调和冷色调的心理感受差异?"},
]

def ds_gen(sp, up, temp=0.7, mt=400):
    body = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":temp}).encode()
    req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Authorization", f"Bearer {DS_KEY}")
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())["choices"][0]["message"]["content"]

def gpt4o_eval(task, ans_a, ans_b, strat_a):
    up = f"Evaluate. Task: {task}\nA ({strat_a}): {ans_a[:300]}\nB (step_by_step): {ans_b[:300]}\nBetter? Output only A or B."
    body = json.dumps({"model":"gpt-4o","messages":[{"role":"user","content":up}],"max_tokens":5,"temperature":0}).encode()
    req = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=body, method="POST")
    req.add_header("Content-Type","application/json"); req.add_header("Authorization", f"Bearer {API2D_KEY}")
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    txt = resp["choices"][0]["message"]["content"].strip().upper()
    return "A" if "A" in txt else ("B" if "B" in txt else ("A" if txt.startswith("A") else "B"))

def check_correctness(response, expected):
    """Simple keyword match for text tasks with known answers."""
    return expected.lower() in response.lower()

def train_phase(name, task_list, initial_weights, rounds, seed, track_correctness=False):
    random.seed(seed)
    w = deepcopy(initial_weights)
    n_tasks = len(task_list)
    wins = 0; correct = 0
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
                wn = gpt4o_eval(tk["q"], o, c, st)
                if wn == "A": wins += 1
                if track_correctness and "answer" in tk:
                    if check_correctness(o, tk["answer"]): correct += 1
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
    print(f"  [{name}] top={top_s}({w[top_s]:.0%}) wins={wins}/{rounds}" + (f" correct={correct}/{rounds}" if track_correctness else ""), flush=True)
    return w, correct if track_correctness else None

def contagion(w_pure, w_contaminated):
    pv=list(w_pure.values()); cv=list(w_contaminated.values())
    diff=sum((a-b)**2 for a,b in zip(pv,cv))**0.5
    norm=sum(v**2 for v in pv)**0.5
    return round(diff/max(0.001,norm),4)

N=3; R=30
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"experiments")
os.makedirs(OUT,exist_ok=True)
CP=os.path.join(OUT,"same_modality_checkpoint.json")

results=[]; start=1
if os.path.exists(CP):
    with open(CP) as f: ck=json.load(f); results=ck.get("results",[]); start=len(results)+1

print(f"\nSame-Modality Controls (T->T, V->V): N={N}, R={R}")
t0=time.time()
init={k:1/len(STRATEGIES) for k in STRATEGIES}

for rep in range(start,N+1):
    sb=rep*10000+R
    print(f"\n--- Rep {rep}/{N} ---",flush=True)
    try:
        # Phase A: Pure text
        w_T, corr_T = train_phase("T", TEXT_TASKS, init, R, sb+1, True)
        # Phase B: Pure visual
        w_V, _ = train_phase("V", VISUAL_TASKS, init, R, sb+2, False)
        # Control C: T->T (same modality continuation)
        w_TT, corr_TT = train_phase("T->T", TEXT_TASKS, w_T, R, sb+3, True)
        # Control D: V->V (same modality continuation)
        w_VV, _ = train_phase("V->V", VISUAL_TASKS, w_V, R, sb+4, False)

        g_TT = contagion(w_T, w_TT)  # inertia text
        g_VV = contagion(w_V, w_VV)  # inertia visual

        r = {"rep":rep, "gTT":g_TT, "gVV":g_VV,
             "corr_T":corr_T, "corr_TT":corr_TT,
             "top_T":max(w_T,key=w_T.get),"top_V":max(w_V,key=w_V.get),
             "top_TT":max(w_TT,key=w_TT.get),"top_VV":max(w_VV,key=w_VV.get),
             "w_T":{k:round(v,3) for k,v in sorted(w_T.items(),key=lambda x:-x[1])},
             "w_V":{k:round(v,3) for k,v in sorted(w_V.items(),key=lambda x:-x[1])},
             "w_TT":{k:round(v,3) for k,v in sorted(w_TT.items(),key=lambda x:-x[1])},
             "w_VV":{k:round(v,3) for k,v in sorted(w_VV.items(),key=lambda x:-x[1])},
             "time":time.time()-t0}
        results.append(r)
        print(f"  g_TT(inertia)={g_TT:.3f} g_VV(inertia)={g_VV:.3f}")
        if corr_T is not None: print(f"  Correctness: T={corr_T}/{R} T->T={corr_TT}/{R}")
        with open(CP,"w") as f: json.dump({"results":results,"last":rep},f,indent=2)
    except Exception as e:
        print(f"ERROR: {e}"); import traceback; traceback.print_exc()
        with open(CP,"w") as f: json.dump({"results":results,"last":rep-1,"error":str(e)},f,indent=2)
        sys.exit(1)

gtt=[r["gTT"] for r in results]; gvv=[r["gVV"] for r in results]
print(f"\nSame-Modality Controls: g_TT(inertia)={sum(gtt)/N:.3f} g_VV(inertia)={sum(gvv)/N:.3f}")
print(f"Compare to cross-modal: gamma ~1.1 (GPT-4o)")
if results and results[0].get("corr_T") is not None:
    cT = [r["corr_T"] for r in results]; cTT = [r["corr_TT"] for r in results]
    print(f"Correctness: T={sum(cT)/len(cT):.1f}/{R} T->T={sum(cTT)/len(cTT):.1f}/{R}")
