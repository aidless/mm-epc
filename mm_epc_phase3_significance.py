"""
MM-EPC Phase 3: Statistical Significance and Extended Contagion
═══════════════════════════════════════════════════════════════
Goal: Run 50-round contagion experiments to establish:
  1. Bootstrap confidence intervals for γ coefficients
  2. p-value for asymmetry (γ_V→T > γ_T→V)
  3. Statistical power analysis
"""

import json, time, urllib.request, random, re, os, math, numpy as np
from copy import deepcopy
from collections import defaultdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── API Keys ──
DS_KEY = ""
DS_EVAL_KEY = ""
DS_EVAL_URL = ""
with open(r"C:\Users\Administrator\Desktop\ai-agent-playground\.env") as f:
    for line in f:
        if m := re.match(r'DEEPSEEK_API_KEY=(.+)', line):
            DS_KEY = m.group(1).strip().strip('"').strip("'")
        if m := re.match(r'DASHSCOPE_KEY=(.+)', line):
            DS_EVAL_KEY = m.group(1).strip().strip('"').strip("'")
        if m := re.match(r'DASHSCOPE_BASE_URL=(.+)', line):
            DS_EVAL_URL = m.group(1).strip().strip('"').strip("'")

# ── LLM Clients ──
def ds(sp, up, temp=0.7, mt=400, retry=3):
    for attempt in range(retry):
        try:
            b = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":temp}).encode()
            r = urllib.request.Request("https://api.deepseek.com/chat/completions", data=b, method="POST")
            r.add_header("Content-Type","application/json")
            r.add_header("Authorization", f"Bearer {DS_KEY}")
            resp = urllib.request.urlopen(r, timeout=30)
            return json.loads(resp.read().decode())["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt == retry-1: raise
            time.sleep(2**attempt)

def qwen_eval(task, ans_a, ans_b, strat_a, retry=3):
    """Qwen3.7-Max as GPT-4o evaluator replacement via DashScope"""
    for attempt in range(retry):
        try:
            up = f"""Evaluate objectively. Task: {task}
A ({strat_a}): {ans_a[:300]}
B (step_by_step): {ans_b[:300]}
Which is better? Output only A or B."""
            b = json.dumps({"model":"gui-plus-2026-02-26","messages":[{"role":"user","content":up}],"max_tokens":5,"temperature":0}).encode()
            r = urllib.request.Request(f"{DS_EVAL_URL}/chat/completions", data=b, method="POST")
            r.add_header("Content-Type","application/json")
            r.add_header("Authorization", f"Bearer {DS_EVAL_KEY}")
            resp = urllib.request.urlopen(r, timeout=35)
            txt = json.loads(resp.read().decode())["choices"][0]["message"]["content"].strip().upper()
            return "A" if "A" in txt else ("B" if "B" in txt else ("A" if txt.startswith("A") else "B"))
        except Exception as e:
            if attempt == retry-1: raise
            time.sleep(2**attempt)

# ── Task Bank ──
TEXT_TASKS = [
    {"mod":"text","q":"1+2*3=?","a":"7"},
    {"mod":"text","q":"5//2=?","a":"2"},
    {"mod":"text","q":"git撤销commit保留修改?","a":"reset --soft"},
    {"mod":"text","q":"写Python回文判断函数。"},
    {"mod":"text","q":"8硬币1假(轻)最少称几次?","a":"2"},
    {"mod":"text","q":"设计URL短链接系统核心组件。"},
    {"mod":"text","q":"索引为何用B+树而非二叉?"},
    {"mod":"text","q":"HTTPS证书验证步骤?"},
    {"mod":"text","q":"Transformer为何比LSTM并行?"},
    {"mod":"text","q":"解释TCP三次握手过程。"},
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
    {"mod":"visual","q":"描述如何画一个流程图表示登录过程。"},
    {"mod":"visual","q":"解释色彩心理学:红色vs蓝色在UI中的应用。"},
]

STRATEGIES = {
    "step_by_step":"逐步推理",
    "critical_check":"先答再审",
    "first_principles":"基本原理",
    "creative_leap":"创新方案",
    "analogy_meta":"类比举例",
    "evidence_cite":"引用依据",
    "synthesis":"综合视角",
    "counterfactual":"反例边界",
    "visual_grounding":"先构建视觉画面再推理",
    "spatial_decompose":"空间/几何组件分解",
    "aesthetic_frame":"美学框架系统评估",
}

# ── Core Training Function ──
def train_phase(name, task_list, initial_weights, rounds, eval_fn):
    w = deepcopy(initial_weights)
    history = []
    
    for i in range(rounds):
        tk = task_list[i % len(task_list)]
        rv = random.random() * sum(w.values())
        cu = 0.0; st = "step_by_step"
        for k, v in w.items():
            cu += v
            if rv <= cu: st = k; break
        
        if (i+1) % 10 == 0 or i == 0:
            print(f"    Round {i+1}/{rounds} (strategy: {st[:12]}...)", flush=True)
        
        try:
            o = ds(f"你是专家AI。策略：{STRATEGIES[st]}", tk["q"])
            c = ds("你是专家AI。策略：逐步推理。", tk["q"])
            wn = eval_fn(tk["q"], o, c, st)
            
            upd = 0.08 if wn == "A" else -0.04
            w[st] += upd
            tot = max(0.01, sum(w.values()))
            w = {k: max(0.01, v/tot) for k, v in w.items()}
            tot = sum(w.values())
            w = {k: v/tot for k, v in w.items()}
            
            history.append({
                "round": i+1,
                "strategy": st,
                "win": wn == "A",
                "weights": {k: round(v, 4) for k, v in w.items()}
            })
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"    Round {i+1} ERROR: {str(e)[:100]}", flush=True)
            history.append({"round": i+1, "error": str(e)[:80]})
    
    return w, history

def l2_norm(w):
    return sum(v**2 for v in w.values())**0.5

def contagion(w_pure, w_contaminated):
    pure_vec = list(w_pure.values())
    cont_vec = list(w_contaminated.values())
    diff = sum((a-b)**2 for a, b in zip(pure_vec, cont_vec))**0.5
    norm = l2_norm(w_pure)
    return round(diff / max(0.001, norm), 4)

def run_full_experiment(repetitions=10, rounds_per_phase=50):
    """Run multiple repetitions to collect statistics, with resume support"""
    incremental_path = r"C:\Users\Administrator\Desktop\aettl-research\experiments\mm_epc_phase3_incremental.json"
    results = []
    
    # Resume: load existing valid results
    if os.path.exists(incremental_path):
        with open(incremental_path) as f:
            existing = json.load(f)
        valid_results = [r for r in existing if r.get("gamma_TV", 0) > 0 or r.get("gamma_VT", 0) > 0]
        results = valid_results
        if valid_results:
            print(f"\n[RESUME] Found {len(valid_results)} completed repetitions, continuing from Rep {len(valid_results)+1}/{repetitions}")
    
    start_rep = len(results)
    
    for rep in range(start_rep, repetitions):
        print(f"\n[Repetition {rep+1}/{repetitions}]")
        t0 = time.time()
        
        # Initialize uniform weights
        init = {k: 1/len(STRATEGIES) for k in STRATEGIES}
        
        # Phase A: Pure text
        print(f"  Phase A: Pure text training...", flush=True)
        w_T, _ = train_phase("pure_text", TEXT_TASKS, init, rounds_per_phase, qwen_eval)
        print(f"  Phase A done ({time.time()-t0:.0f}s)", flush=True)
        
        # Phase B: Pure visual
        print(f"  Phase B: Pure visual training...", flush=True)
        w_V, _ = train_phase("pure_visual", VISUAL_TASKS, init, rounds_per_phase, qwen_eval)
        print(f"  Phase B done ({time.time()-t0:.0f}s)", flush=True)
        
        # Phase C: Contagion T → V
        print(f"  Phase C: Contagion T->V...", flush=True)
        w_TV, _ = train_phase("contagion_TV", VISUAL_TASKS, w_T, rounds_per_phase, qwen_eval)
        print(f"  Phase C done ({time.time()-t0:.0f}s)", flush=True)
        
        # Phase D: Contagion V → T
        print(f"  Phase D: Contagion V->T...", flush=True)
        w_VT, _ = train_phase("contagion_VT", TEXT_TASKS, w_V, rounds_per_phase, qwen_eval)
        print(f"  Phase D done ({time.time()-t0:.0f}s)", flush=True)
        
        # Calculate coefficients
        gamma_TV = contagion(w_V, w_TV)
        gamma_VT = contagion(w_T, w_VT)
        asymmetry = abs(gamma_TV - gamma_VT) / max(0.001, gamma_TV + gamma_VT)
        
        # Record results
        results.append({
            "repetition": rep+1,
            "gamma_TV": gamma_TV,
            "gamma_VT": gamma_VT,
            "asymmetry": asymmetry,
            "asymmetric": gamma_TV != gamma_VT,
            "direction": "V→T" if gamma_VT > gamma_TV else "T→V",
            "w_T_top": max(w_T, key=w_T.get),
            "w_V_top": max(w_V, key=w_V.get),
            "w_TV_top": max(w_TV, key=w_TV.get),
            "w_VT_top": max(w_VT, key=w_VT.get),
            "time": time.time() - t0,
        })
        
        # Save incremental results
        with open(r"C:\Users\Administrator\Desktop\aettl-research\experiments\mm_epc_phase3_incremental.json", "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

def bootstrap_analysis(results, n_bootstrap=10000):
    """Bootstrap confidence intervals and p-value for asymmetry"""
    gamma_TV_vals = [r["gamma_TV"] for r in results]
    gamma_VT_vals = [r["gamma_VT"] for r in results]
    
    # Bootstrap resampling
    bootstrap_diffs = []
    n = len(results)
    
    for _ in range(n_bootstrap):
        idxs = np.random.choice(n, n, replace=True)
        diff = np.mean([gamma_VT_vals[i] for i in idxs]) - np.mean([gamma_TV_vals[i] for i in idxs])
        bootstrap_diffs.append(diff)
    
    # Calculate statistics
    mean_diff = np.mean(gamma_VT_vals) - np.mean(gamma_TV_vals)
    ci_lower = np.percentile(bootstrap_diffs, 2.5)
    ci_upper = np.percentile(bootstrap_diffs, 97.5)
    
    # One-sided p-value (H0: γ_VT ≤ γ_TV, H1: γ_VT > γ_TV)
    p_value = np.mean([d <= 0 for d in bootstrap_diffs])
    
    return {
        "mean_gamma_TV": float(np.mean(gamma_TV_vals)),
        "mean_gamma_VT": float(np.mean(gamma_VT_vals)),
        "mean_diff": float(mean_diff),
        "ci_95": [float(ci_lower), float(ci_upper)],
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
        "n_repetitions": int(n),
        "std_gamma_TV": float(np.std(gamma_TV_vals)),
        "std_gamma_VT": float(np.std(gamma_VT_vals)),
    }

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  MM-EPC Phase 3: Statistical Significance and Power        ║
║  Repetitions: 10 × (50 rounds × 4 phases) = 2000 LLM calls ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Create output directory
    os.makedirs(r"C:\Users\Administrator\Desktop\aettl-research\experiments", exist_ok=True)
    
    # Run experiments
    results = run_full_experiment(repetitions=10, rounds_per_phase=50)
    
    # Statistical analysis
    stats_result = bootstrap_analysis(results)
    
    # Save final results
    final_output = {
        "phase": "3_significance",
        "repetitions": len(results),
        "rounds_per_phase": 50,
        "total_llm_calls": len(results) * 50 * 4,
        "raw_results": results,
        "statistical_analysis": stats_result,
        "summary": {
            "gamma_TV_mean": round(stats_result["mean_gamma_TV"], 4),
            "gamma_TV_std": round(stats_result["std_gamma_TV"], 4),
            "gamma_VT_mean": round(stats_result["mean_gamma_VT"], 4),
            "gamma_VT_std": round(stats_result["std_gamma_VT"], 4),
            "mean_difference": round(stats_result["mean_diff"], 4),
            "ci_95_lower": round(stats_result["ci_95"][0], 4),
            "ci_95_upper": round(stats_result["ci_95"][1], 4),
            "p_value": round(stats_result["p_value"], 4),
            "significant": stats_result["significant"],
        }
    }
    
    with open(r"C:\Users\Administrator\Desktop\aettl-research\experiments\mm_epc_phase3_final.json", "w") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("STATISTICAL SUMMARY")
    print("="*60)
    print(f"γ_T→V: {final_output['summary']['gamma_TV_mean']:.4f} ± {final_output['summary']['gamma_TV_std']:.4f}")
    print(f"γ_V→T: {final_output['summary']['gamma_VT_mean']:.4f} ± {final_output['summary']['gamma_VT_std']:.4f}")
    print(f"Difference (V→T - T→V): {final_output['summary']['mean_difference']:.4f}")
    print(f"95% CI: [{final_output['summary']['ci_95_lower']:.4f}, {final_output['summary']['ci_95_upper']:.4f}]")
    print(f"One-sided p-value: {final_output['summary']['p_value']:.4f}")
    print(f"Significant (p<0.05): {final_output['summary']['significant']}")
    print("="*60)
    
    return final_output

if __name__ == "__main__":
    main()