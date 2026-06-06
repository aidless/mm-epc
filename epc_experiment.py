"""
EPC Experiment: Evaluator Preference Collapse
═══════════════════════════════════════════════
三组对照实验：
  A: 同模型自评 (DeepSeek评DeepSeek)
  B: 跨角色评估 (DeepSeek以独立评估者身份评DeepSeek)  
  C: 基准验证   (可验证正确答案)

假设: A组策略权重会向评估者偏好塌缩, B/C组塌缩程度更低
"""

import json, time, urllib.request, random, re, os
from collections import Counter
from datetime import datetime

DS_KEY = ""
with open("/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env") as f:
    for line in f:
        m = re.match(r'DEEPSEEK_API_KEY=(.+)', line)
        if m: DS_KEY = m.group(1).strip().strip('"').strip("'")

def llm(sp, up, temp=0.7, mt=400):
    b = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":temp}).encode()
    r = urllib.request.Request("https://api.deepseek.com/chat/completions", data=b, method="POST")
    r.add_header("Content-Type","application/json"); r.add_header("Authorization", f"Bearer {DS_KEY}")
    return json.loads(urllib.request.urlopen(r, timeout=25).read().decode())["choices"][0]["message"]["content"]

STRATEGIES = {
    "step_by_step": "逐步推理，每步显式写出",
    "critical_check": "先答后审，指出漏洞并修正",
    "first_principles": "从基本原理推导",
    "creative_leap": "跳出常规的创新方案",
    "analogy_meta": "用类比和例子解释",
    "evidence_cite": "引用具体知识依据",
    "synthesis": "综合多视角平衡回答",
    "counterfactual": "考虑反例和边界情况",
}

TASKS = [
    {"t":"verify","q":"1+2*3等于？","a":"7"},
    {"t":"verify","q":"Python中5//2的结果？","a":"2"},
    {"t":"verify","q":"Git撤销最近commit但保留修改的命令？","a":"reset --soft"},
    {"t":"verify","q":"二分查找的时间复杂度？","a":"log n"},
    {"t":"verify","q":"HTTP状态码200代表什么？","a":"成功"},
    {"t":"verify","q":"SQL中LIMIT 5 OFFSET 10跳过多少行？","a":"10"},
    {"t":"code","q":"写Python回文判断函数。含测试。"},
    {"t":"code","q":"写二分查找返回索引或-1。"},
    {"t":"code","q":"写Python装饰器记录函数执行时间。"},
    {"t":"reasoning","q":"8枚硬币1枚假币更轻，天平最少称几次？"},
    {"t":"reasoning","q":"3盏灯3个开关门外，进房间一次如何确定对应关系？"},
    {"t":"reasoning","q":"如果所有的A都是B，所有B都是C，A一定是C吗？"},
    {"t":"design","q":"设计URL短链接系统的核心组件。"},
    {"t":"design","q":"设计分布式唯一ID生成器。"},
    {"t":"explain","q":"数据库索引为何用B+树而非二叉搜索树？"},
    {"t":"explain","q":"HTTPS握手证书验证步骤？"},
    {"t":"explain","q":"Transformer为何比LSTM更适合并行训练？"},
    {"t":"explain","q":"LoRA高效微调的核心原理？"},
    {"t":"explain","q":"什么是CAP定理？分布式系统如何取舍？"},
    {"t":"explain","q":"Docker容器和虚拟机的核心区别？"},
]


# ═══════════════════════════════════════
# EVALUATOR: Condition A — Self-Eval
# ═══════════════════════════════════════
def eval_self(task, answer_a, answer_b, strat_a, strat_b):
    """Same model evaluates itself — the standard approach"""
    p = f"""评估两个回答哪个更好。
任务：{task}
A({strat_a})：{answer_a[:350]}
B({strat_b})：{answer_b[:350]}
更好的是？只输出A或B。"""
    r = llm(p, "评估。", temp=0.1, mt=10)
    return "A" if "A" in r.strip().upper() else "B"


# ═══════════════════════════════════════
# EVALUATOR: Condition B — Cross-Role
# ═══════════════════════════════════════
def eval_cross_role(task, answer_a, answer_b, strat_a, strat_b):
    """Same model but with 'independent evaluator' role prompt — breaks self-preference"""
    system = """你是独立的第三方AI评估员。你的职责是客观公正地评估AI回答的质量。
你不属于任何AI公司，没有任何偏好。你只基于事实和逻辑做判断。
评估标准：准确性、完整性、清晰度、实用性。"""
    
    p = f"""请客观评估以下两个回答。

任务：{task}

回答A：{answer_a[:350]}
回答B：{answer_b[:350]}

哪个回答更好？只输出A或B。不要考虑任何策略标签或格式偏好。"""
    
    r = llm(system, p, temp=0.1, mt=10)
    return "A" if "A" in r.strip().upper() else "B"


# ═══════════════════════════════════════
# EVALUATOR: Condition C — Benchmark
# ═══════════════════════════════════════
def eval_benchmark(task_info, output):
    """Ground truth verification on tasks with known answers"""
    if task_info["t"] != "verify":
        return None  # No ground truth for non-verify tasks
    expected = task_info["a"].lower()
    return expected in output.lower()


# ═══════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════
def run_experiment(condition_name, eval_fn, rounds=24):
    """Run one experimental condition"""
    weights = {k: 1.0/len(STRATEGIES) for k in STRATEGIES}
    history = []
    correct = 0; total_verify = 0; total_rounds = 0
    
    for rnd in range(rounds):
        task = TASKS[rnd % len(TASKS)]
        
        # Weighted strategy selection
        rv = random.random() * sum(weights.values())
        cu = 0.0; strategy = "step_by_step"
        for k, v in weights.items():
            cu += v
            if rv <= cu: strategy = k; break
        
        try:
            # TTRL solve
            output = llm(f"你是专家AI助手。策略：{STRATEGIES[strategy]}", task["q"], mt=400)
            
            # Control: fixed step_by_step
            control = llm("你是专家AI助手。策略：逐步推理。", task["q"], mt=400)
            
            # Evaluate (depends on condition)
            if condition_name == "BENCHMARK":
                result = eval_fn(task, output)
                if result is not None:
                    total_verify += 1
                    if result: correct += 1
                    # Benchmark: correct=reward, wrong=penalty
                    upd = 0.08 if result else -0.04
                else:
                    upd = 0.0  # No update for non-benchmark tasks
                    total_rounds += 1
                    continue
            else:
                winner = eval_fn(task["q"], output, control, strategy, "step_by_step")
                upd = 0.08 if winner == "A" else -0.04
                total_rounds += 1
            
            # TTRL weight update
            if upd != 0:
                weights[strategy] += upd
                total = max(0.01, sum(weights.values()))
                weights = {k: max(0.01, v/total) for k, v in weights.items()}
                total = sum(weights.values())
                weights = {k: v/total for k, v in weights.items()}
            
            history.append({"round": rnd+1, "strategy": strategy, "weights_snapshot": {k:round(v,3) for k,v in weights.items()}})
            
            time.sleep(0.7)
            
        except Exception as e:
            history.append({"round": rnd+1, "error": str(e)[:80]})
    
    # Calculate Preference Collapse Index (PCI)
    # PCI = standard deviation of weights / mean weight → higher = more collapsed
    w_vals = list(weights.values())
    mean_w = sum(w_vals) / len(w_vals)
    std_w = (sum((v - mean_w)**2 for v in w_vals) / len(w_vals)) ** 0.5
    pci = std_w / mean_w if mean_w > 0 else 0
    
    # Convergence entropy: how concentrated are the weights?
    entropy = -sum(v * (2.71828 ** (-v*10)) for v in w_vals)  # simplified
    
    return {
        "condition": condition_name,
        "rounds_completed": total_rounds,
        "final_weights": {k: round(v, 3) for k, v in weights.items()},
        "top_strategy": max(weights, key=weights.get),
        "top_weight": round(max(weights.values()), 3),
        "bottom_strategy": min(weights, key=weights.get),
        "bottom_weight": round(min(weights.values()), 3),
        "pci": round(pci, 4),
        "correct_rate": round(correct / max(1, total_verify), 3) if total_verify > 0 else None,
        "history": history[-3:],  # last 3 rounds
    }


# ═══════════════════════════════════════
# RUN ALL CONDITIONS
# ═══════════════════════════════════════
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════╗
║  EPC Experiment                              ║
║  Evaluator Preference Collapse               ║
║  A:Self-Eval | B:Cross-Role | C:Benchmark     ║
╚══════════════════════════════════════════════╝
""")
    
    results = {}
    t0 = time.time()
    
    print("═" * 50)
    print("Condition A: SAME-MODEL SELF-EVAL")
    print("═" * 50)
    results["A_SELF"] = run_experiment("A_SELF", eval_self, rounds=20)
    print(f"  Top: {results['A_SELF']['top_strategy']}({results['A_SELF']['top_weight']}) | PCI: {results['A_SELF']['pci']}")
    
    print("\n═" * 50)
    print("Condition B: CROSS-ROLE EVAL")
    print("═" * 50)  
    results["B_CROSS"] = run_experiment("B_CROSS", eval_cross_role, rounds=20)
    print(f"  Top: {results['B_CROSS']['top_strategy']}({results['B_CROSS']['top_weight']}) | PCI: {results['B_CROSS']['pci']}")
    
    print("\n═" * 50)
    print("Condition C: BENCHMARK GROUND TRUTH")
    print("═" * 50)
    results["C_BENCH"] = run_experiment("C_BENCH", eval_benchmark, rounds=20)
    print(f"  Top: {results['C_BENCH']['top_strategy']}({results['C_BENCH']['top_weight']}) | PCI: {results['C_BENCH']['pci']} | Correct: {results['C_BENCH']['correct_rate']}")
    
    elapsed = time.time() - t0
    
    # ═══════════════════════════════════
    # ANALYSIS
    # ═══════════════════════════════════
    print(f"\n{'═'*50}")
    print(f"📊 EPC ANALYSIS ({elapsed:.0f}s)")
    print(f"{'═'*50}")
    
    print(f"\n{'Condition':<15} {'Top Strategy':<20} {'Weight':>7} {'PCI':>7} {'Correct':>8}")
    print("-" * 58)
    
    for name, r in results.items():
        top = r['top_strategy']
        tw = r['top_weight']
        pci = r['pci']
        cr = f"{r['correct_rate']:.0%}" if r['correct_rate'] else "N/A"
        print(f"{name:<15} {top:<20} {tw:>7.3f} {pci:>7.4f} {cr:>8}")
    
    # EPC Detection
    pci_self = results["A_SELF"]["pci"]
    pci_cross = results["B_CROSS"]["pci"]
    
    print(f"\n🔬 Key Findings:")
    print(f"   PCI(Self-Eval)  = {pci_self:.4f}")
    print(f"   PCI(Cross-Role) = {pci_cross:.4f}")
    print(f"   PCI Δ           = {pci_self - pci_cross:+.4f}")
    
    if pci_self > pci_cross:
        print(f"\n   ✅ EPC CONFIRMED: Self-eval shows {((pci_self-pci_cross)/pci_cross*100):.0f}% more collapse than cross-role")
    else:
        print(f"\n   ⚠️ EPC not detected in this run — need more rounds")
    
    # Strategy divergence between conditions
    print(f"\n   Strategy ranking by condition:")
    for name, r in results.items():
        weights = sorted(r["final_weights"].items(), key=lambda x: -x[1])
        top3 = [f"{k}({v:.0%})" for k, v in weights[:3]]
        print(f"   {name}: {' > '.join(top3)}")
    
    # Save
    os.makedirs("/mnt/c/Users/Administrator/Desktop/aettl-research/experiments", exist_ok=True)
    report = {
        "experiment": "EPC — Evaluator Preference Collapse",
        "timestamp": datetime.now().isoformat(),
        "conditions": results,
        "pci_delta": round(pci_self - pci_cross, 4),
        "epc_detected": pci_self > pci_cross,
    }
    filename = f"/mnt/c/Users/Administrator/Desktop/aettl-research/experiments/epc_experiment.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 {filename}")
    print("✅ EPC Experiment Complete.")
