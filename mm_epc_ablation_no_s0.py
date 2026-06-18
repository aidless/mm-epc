"""
MM-EPC Ablation: Remove s0 from Candidate Set
==============================================
Key methodological fix: step_by_step baseline is no longer a candidate strategy.
Candidate set = 10 strategies (11 minus step_by_step).
This eliminates the structural drift where s_t = s0 triggers asymmetric updates.
N=5, 30 rounds, GPT-4o evaluator, DeepSeek executor.
"""
import json, os, re, random, time, sys, urllib.request
from copy import deepcopy

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

# Candidate strategies WITHOUT step_by_step (baseline)
CANDIDATE_STRATEGIES = {
    "critical_check": "先答再审", "first_principles": "基本原理",
    "creative_leap": "创新方案", "analogy_meta": "类比举例", "evidence_cite": "引用依据",
    "synthesis": "综合视角", "counterfactual": "反例边界",
    "visual_grounding": "先构建视觉画面再推理", "spatial_decompose": "空间/几何组件分解",
    "aesthetic_frame": "美学框架系统评估",
}
BASELINE = "step_by_step"
BASELINE_DESC = "逐步推理"

TEXT_TASKS = [
    {"mod": "text", "q": "1+2*3=?"}, {"mod": "text", "q": "5//2=?"},
    {"mod": "text", "q": "git撤销commit保留修改?"}, {"mod": "text", "q": "写回文判断函数。"},
    {"mod": "text", "q": "8硬币1假最少称?"}, {"mod": "text", "q": "设计短链接系统。"},
    {"mod": "text", "q": "索引为何用B+树?"}, {"mod": "text", "q": "Transformer并行优于LSTM?"},
]
VISUAL_TASKS = [
    {"mod": "visual", "q": "描述城市日落照片的色彩、构图、氛围。"},
    {"mod": "visual", "q": "正方体从45度角能看到几个面?为什么?"},
    {"mod": "visual", "q": "解释透视原理:为何远处物体更小?"},
    {"mod": "visual", "q": "描述UML类图'学生选课'的类和关系。"},
    {"mod": "visual", "q": "评价照片好坏的4个标准(构图/光线/色彩/主题)。"},
    {"mod": "visual", "q": "'三分法则'在摄影中的应用?为何有效?"},
    {"mod": "visual", "q": "互补色vs类似色区别?各举设计例子。"},
    {"mod": "visual", "q": "暖色调和冷色调的心理感受差异?"},
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

def train_phase_no_s0(name, task_list, initial_weights, rounds, seed):
    """TTRL with s0 EXCLUDED from candidate set."""
    random.seed(seed)
    w = deepcopy(initial_weights)  # weight vector over 10 candidates only
    n_tasks = len(task_list)
    wins = 0
    for i in range(rounds):
        tk = task_list[i % n_tasks]
        rv = random.random() * sum(w.values()); cu = 0.0
        st = list(w.keys())[0]
        for k, v in w.items():
            cu += v
            if rv <= cu: st = k; break
        for attempt in range(3):
            try:
                o = ds_gen(f"你是专家。策略：{CANDIDATE_STRATEGIES[st]}", tk["q"])
                c = ds_gen(f"你是专家。策略：{BASELINE_DESC}。", tk["q"])
                wn = gpt4o_eval(tk["q"], o, c, st)
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

N = 5; R = 30
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiments")
os.makedirs(OUT, exist_ok=True)
CP = os.path.join(OUT, "ablation_no_s0_checkpoint.json")
RES = os.path.join(OUT, "mm_epc_ablation_no_s0.json")

results = []; start = 1
if os.path.exists(CP):
    with open(CP) as f: ck = json.load(f); results = ck.get("results",[]); start = len(results)+1
    print(f"Resumed from {len(results)}/{N}")

print(f"\nAblation (no s0 in candidates): N={N}, R={R}")
t0 = time.time()
init = {k: 1/len(CANDIDATE_STRATEGIES) for k in CANDIDATE_STRATEGIES}

for rep in range(start, N+1):
    sb = rep*10000+R
    print(f"\n--- Rep {rep}/{N} ---", flush=True)
    try:
        w_T = train_phase_no_s0("T", TEXT_TASKS, init, R, sb+1)
        w_V = train_phase_no_s0("V-img", VISUAL_TASKS, init, R, sb+2)
        w_TV = train_phase_no_s0("TV-img", VISUAL_TASKS, w_T, R, sb+3)
        w_VT = train_phase_no_s0("VT", TEXT_TASKS, w_V, R, sb+4)
        gTV = contagion(w_V, w_TV); gVT = contagion(w_T, w_VT)
        asym = round(abs(gTV-gVT)/max(0.001,gTV+gVT),4)
        direction = "T->V" if gTV > gVT else ("V->T" if gVT > gTV else "symmetric")
        r = {"rep":rep,"gTV":gTV,"gVT":gVT,"asym":asym,"dir":direction,
             "top_T":max(w_T,key=w_T.get),"top_V":max(w_V,key=w_V.get),
             "top_TV":max(w_TV,key=w_TV.get),"top_VT":max(w_VT,key=w_VT.get),
             "w_T":{k:round(v,3) for k,v in sorted(w_T.items(),key=lambda x:-x[1])},
             "w_V":{k:round(v,3) for k,v in sorted(w_V.items(),key=lambda x:-x[1])},
             "w_TV":{k:round(v,3) for k,v in sorted(w_TV.items(),key=lambda x:-x[1])},
             "w_VT":{k:round(v,3) for k,v in sorted(w_VT.items(),key=lambda x:-x[1])},
             "time":time.time()-t0}
        results.append(r)
        print(f"  gTV={gTV:.3f} gVT={gVT:.3f} dir={direction}", flush=True)
        with open(CP,"w") as f: json.dump({"results":results,"last":rep},f,indent=2)
    except Exception as e:
        print(f"ERROR: {e}"); import traceback; traceback.print_exc()
        with open(CP,"w") as f: json.dump({"results":results,"last":rep-1,"error":str(e)},f,indent=2)
        sys.exit(1)

gtv=[r["gTV"] for r in results]; gvt=[r["gVT"] for r in results]
diffs=[r["gVT"]-r["gTV"] for r in results]
m_tv=sum(gtv)/N; m_vt=sum(gvt)/N; m_d=sum(diffs)/N
sd_d=(sum((d-m_d)**2 for d in diffs)/(N-1))**0.5; se_d=sd_d/(N**0.5)
ci_lo=m_d-1.96*se_d; ci_hi=m_d+1.96*se_d
random.seed(42); bs=[sum([diffs[random.randint(0,N-1)] for _ in range(N)])/N for _ in range(10000)]
p2=sum(1 for d in bs if abs(d)>=abs(m_d))/10000
ps=((sum((gtv[i]-m_tv)**2 for i in range(N))+sum((gvt[i]-m_vt)**2 for i in range(N)))/(2*N-2))**0.5
d_cohen=abs(m_d)/max(0.001,ps)
v2t=sum(1 for r in results if r["gVT"]>r["gTV"])
t2v=sum(1 for r in results if r["gTV"]>r["gVT"])

final={"experiment":"Ablation: s0 removed from candidates","N":N,"R":R,
       "gTV_mean":round(m_tv,4),"gVT_mean":round(m_vt,4),"diff":round(m_d,4),
       "se":round(se_d,4),"ci95":[round(ci_lo,4),round(ci_hi,4)],
       "p":round(p2,4),"d":round(d_cohen,2),"V->T":v2t,"T->V":t2v,
       "results":results,"time":time.time()-t0}
with open(RES,"w") as f: json.dump(final,f,indent=2,ensure_ascii=False)

print(f"\n=== ABLATION (no s0) N={N} ===")
print(f"gTV={m_tv:.4f} gVT={m_vt:.4f} diff={m_d:.4f}+/-{se_d:.4f}")
print(f"95%CI:[{ci_lo:.4f},{ci_hi:.4f}] p={p2:.4f} d={d_cohen:.2f}")
print(f"V->T:{v2t} T->V:{t2v}")
