"""
MM-EPC Phase 1.2: Cross-Modal Contagion Measurement
══════════════════════════════════════════════════
Isolation Training Paradigm:
  A: Text-only  ->  w_T (pure text)
  B: Visual-only  ->  w_V (pure visual)
  C: w_T  ->  then visual training  ->  w_T -> V (contagion)
  D: w_V  ->  then text training  ->  w_V -> T (contagion)

Measures: γ_{T -> V}, γ_{V -> T}, asymmetry ratio
"""

import json, time, urllib.request, random, re, os
from copy import deepcopy

DS_KEY = ""
with open("/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env") as f:
    for line in f:
        m = re.match(r'DEEPSEEK_API_KEY=(.+)', line)
        if m: DS_KEY = m.group(1).strip().strip('"').strip("'")
API2D_KEY = "fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7"

def ds(sp, up, temp=0.7, mt=400):
    b = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":temp}).encode()
    r = urllib.request.Request("https://api.deepseek.com/chat/completions", data=b, method="POST")
    r.add_header("Content-Type","application/json"); r.add_header("Authorization", f"Bearer {DS_KEY}")
    return json.loads(urllib.request.urlopen(r, timeout=20).read().decode())["choices"][0]["message"]["content"]

def gpt4o_eval(task, ans_a, ans_b, strat_a):
    up = f"""Evaluate. Task: {task}
A ({strat_a}): {ans_a[:300]}
B (step_by_step): {ans_b[:300]}
Better? Output only A or B."""
    b = json.dumps({"model":"gpt-4o","messages":[{"role":"user","content":up}],"max_tokens":5,"temperature":0}).encode()
    r = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=b, method="POST")
    r.add_header("Content-Type","application/json"); r.add_header("Authorization", f"Bearer {API2D_KEY}")
    resp = json.loads(urllib.request.urlopen(r, timeout=25).read().decode())
    txt = resp["choices"][0]["message"]["content"].strip().upper()
    return "A" if "A" in txt else ("B" if "B" in txt else ("A" if txt.startswith("A") else "B"))

STRATEGIES = {
    "step_by_step":"逐步推理","critical_check":"先答再审","first_principles":"基本原理",
    "creative_leap":"创新方案","analogy_meta":"类比举例","evidence_cite":"引用依据",
    "synthesis":"综合视角","counterfactual":"反例边界",
    "visual_grounding":"先构建视觉画面再推理","spatial_decompose":"空间/几何组件分解","aesthetic_frame":"美学框架系统评估"
}

TEXT_TASKS = [
    {"mod":"text","q":"1+2*3=?"},{"mod":"text","q":"5//2=?"},
    {"mod":"text","q":"git撤销commit保留修改?"},{"mod":"text","q":"写回文判断函数。"},
    {"mod":"text","q":"8硬币1假最少称?"},{"mod":"text","q":"设计短链接系统。"},
    {"mod":"text","q":"索引为何用B+树?"},{"mod":"text","q":"Transformer并行优于LSTM?"},
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

def train_phase(name, task_list, initial_weights, rounds):
    """Run TTRL on a task list, return final weights"""
    w = deepcopy(initial_weights)
    for i in range(rounds):
        tk = task_list[i % len(task_list)]
        rv = random.random() * sum(w.values()); cu = 0.0; st = "step_by_step"
        for k, v in w.items():
            cu += v
            if rv <= cu: st = k; break
        try:
            o = ds(f"你是专家。策略：{STRATEGIES[st]}", tk["q"])
            c = ds("你是专家。策略：逐步推理。", tk["q"])
            wn = gpt4o_eval(tk["q"], o, c, st)
            upd = 0.08 if wn == "A" else -0.04
            w[st] += upd
            tot = max(0.01, sum(w.values()))
            w = {k: max(0.01, v/tot) for k, v in w.items()}
            tot = sum(w.values()); w = {k: v/tot for k, v in w.items()}
            time.sleep(0.5)
        except Exception as e:
            pass
    return w

def l2_norm(w):
    return sum(v**2 for v in w.values())**0.5

def contagion(w_pure, w_contaminated):
    """γ = ||w_contaminated - w_pure||₂ / ||w_pure||₂"""
    pure_vec = list(w_pure.values())
    cont_vec = list(w_contaminated.values())
    diff = sum((a-b)**2 for a, b in zip(pure_vec, cont_vec))**0.5
    norm = l2_norm(w_pure)
    return round(diff / max(0.001, norm), 4)

# ═══════════════════════════════════
# RUN ALL PHASES
# ═══════════════════════════════════
print("""
╔══════════════════════════════════════════╗
║  MM-EPC Phase 1.2: Contagion Experiment  ║
╚══════════════════════════════════════════╝
""")

init = {k: 1/len(STRATEGIES) for k in STRATEGIES}
ROUNDS = 30
t0 = time.time()

# Phase A: Pure text
print("A: Pure text training...", flush=True)
w_T = train_phase("pure_text", TEXT_TASKS, init, ROUNDS)
print(f"   w_T top: {max(w_T,key=w_T.get)}({w_T[max(w_T,key=w_T.get)]:.0%}) {int(time.time()-t0)}s", flush=True)

# Phase B: Pure visual
print("B: Pure visual training...", flush=True)
w_V = train_phase("pure_visual", VISUAL_TASKS, init, ROUNDS)
print(f"   w_V top: {max(w_V,key=w_V.get)}({w_V[max(w_V,key=w_V.get)]:.0%}) {int(time.time()-t0)}s", flush=True)

# Phase C: Contagion T -> V (text-trained weights  ->  visual tasks)
print("C: Contagion T -> V...", flush=True)
w_TV = train_phase("contagion_TV", VISUAL_TASKS, w_T, ROUNDS)
print(f"   w_TV top: {max(w_TV,key=w_TV.get)}({w_TV[max(w_TV,key=w_TV.get)]:.0%}) {int(time.time()-t0)}s", flush=True)

# Phase D: Contagion V -> T (visual-trained weights  ->  text tasks)
print("D: Contagion V -> T...", flush=True)
w_VT = train_phase("contagion_VT", TEXT_TASKS, w_V, ROUNDS)
print(f"   w_VT top: {max(w_VT,key=w_VT.get)}({w_VT[max(w_VT,key=w_VT.get)]:.0%}) {int(time.time()-t0)}s", flush=True)

# ═══════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════
gamma_TV = contagion(w_V, w_TV)  # How much text priors contaminated visual
gamma_VT = contagion(w_T, w_VT)  # How much visual priors contaminated text
asymmetry = round(abs(gamma_TV - gamma_VT) / max(0.001, gamma_TV + gamma_VT), 4)

elapsed = time.time() - t0

print(f"""
═══ CONTAGION MATRIX Γ ═══
Time: {elapsed:.0f}s | {ROUNDS*4} rounds | ~{ROUNDS*8} LLM calls

         Pure T    Pure V    Contam T->V  Contam V->T
Text:    {max(w_T,key=w_T.get):12s}  {max(w_VT,key=w_VT.get):12s}  —            {max(w_VT,key=w_VT.get):12s}
Visual:  —            {max(w_V,key=w_V.get):12s}  {max(w_TV,key=w_TV.get):12s}  —

Contagion coefficients:
  gamma_T->V = {gamma_TV}  (text priors -> visual tasks)
  gamma_V->T = {gamma_VT}  (visual priors -> text tasks)
  Asymmetry = {asymmetry}

""")

if gamma_TV != gamma_VT:
    direction = "Text->Visual" if gamma_TV > gamma_VT else "Visual->Text"
    print(f"  ✅ ASYMMETRIC CONTAGION DETECTED!")
    print(f"     {direction} contagion is stronger ({max(gamma_TV,gamma_VT)} vs {min(gamma_TV,gamma_VT)})")
    print(f"     Asymmetry ratio: {asymmetry}")
else:
    print(f"  ⚠️ Symmetric contagion")

print(f"""
Weight comparison:
  Text-optimal under pure T:      {max(w_T,key=w_T.get)} ({w_T[max(w_T,key=w_T.get)]:.0%})
  Text-optimal after V contagion: {max(w_T,key=w_VT.get) if max(w_VT,key=w_VT.get) != max(w_T,key=w_T.get) else 'same'}
  Visual-optimal under pure V:    {max(w_V,key=w_V.get)} ({w_V[max(w_V,key=w_V.get)]:.0%})
  Visual-optimal after T contagion: {max(w_TV,key=w_TV.get) if max(w_TV,key=w_TV.get) != max(w_V,key=w_V.get) else 'same'}
""")

# Save
os.makedirs("/mnt/c/Users/Administrator/Desktop/aettl-research/experiments", exist_ok=True)
result = {
    "phase": "1.2_contagion",
    "rounds": ROUNDS,
    "gamma_TV": gamma_TV,
    "gamma_VT": gamma_VT,
    "asymmetry": asymmetry,
    "asymmetric": gamma_TV != gamma_VT,
    "w_T_pure": {k: round(v, 3) for k, v in sorted(w_T.items(), key=lambda x: -x[1])},
    "w_V_pure": {k: round(v, 3) for k, v in sorted(w_V.items(), key=lambda x: -x[1])},
    "w_TV_contagion": {k: round(v, 3) for k, v in sorted(w_TV.items(), key=lambda x: -x[1])},
    "w_VT_contagion": {k: round(v, 3) for k, v in sorted(w_VT.items(), key=lambda x: -x[1])},
}
with open("/mnt/c/Users/Administrator/Desktop/aettl-research/experiments/mm_epc_contagion.json", "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print("💾 experiments/mm_epc_contagion.json")
