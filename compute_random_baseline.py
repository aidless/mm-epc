"""
Random Baseline PCI Computation
-------------------------------
Simulates TTRL with a random/shuffled evaluator (50/50 A/B choice).
No API calls needed - purely computational.
Runs N repetitions to get stable mean and confidence interval.
"""

import random, json, os, math
from copy import deepcopy

STRATEGIES = {
    "step_by_step": "逐步推理", "critical_check": "先答再审", "first_principles": "基本原理",
    "creative_leap": "创新方案", "analogy_meta": "类比举例", "evidence_cite": "引用依据",
    "synthesis": "综合视角", "counterfactual": "反例边界",
    "visual_grounding": "先构建视觉画面再推理", "spatial_decompose": "空间/几何组件分解",
    "aesthetic_frame": "美学框架系统评估"
}

def compute_pci(weights):
    """PCI = sigma(w) / mu(w)"""
    vals = list(weights.values())
    mu = sum(vals) / len(vals)
    if mu < 1e-10:
        return 0.0
    sigma = (sum((v - mu)**2 for v in vals) / len(vals)) ** 0.5
    return sigma / mu

def train_phase_random(task_list, initial_weights, rounds):
    """Run TTRL with random evaluator (50/50 coin flip)"""
    w = deepcopy(initial_weights)
    n_tasks = len(task_list)
    alpha_win, alpha_lose = 0.08, -0.04

    for i in range(rounds):
        # Sample a strategy
        rv = random.random() * sum(w.values())
        cum = 0.0
        st = "step_by_step"
        for k, v in w.items():
            cum += v
            if rv <= cum:
                st = k
                break

        # Random evaluator: 50% win, 50% lose
        if random.random() < 0.5:
            upd = alpha_win
        else:
            upd = alpha_lose

        w[st] = max(0.001, w[st] + upd)
        tot = sum(w.values())
        w = {k: v / tot for k, v in w.items()}

    return w

# Tasks (same as Phase 2 for fair comparison)
TEXT_TASKS = [
    {"mod": "text", "q": "1+2*3=?"},
    {"mod": "text", "q": "5//2=?"},
    {"mod": "text", "q": "git撤销commit保留修改?"},
    {"mod": "text", "q": "写回文判断函数。"},
    {"mod": "text", "q": "8硬币1假最少称?"},
    {"mod": "text", "q": "设计短链接系统。"},
    {"mod": "text", "q": "索引为何用B+树?"},
    {"mod": "text", "q": "Transformer并行优于LSTM?"},
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

ALL_TASKS = TEXT_TASKS + VISUAL_TASKS

init = {k: 1 / len(STRATEGIES) for k in STRATEGIES}

# Run N repetitions with different random seeds
N = 100  # Many repetitions since this is fast (no API calls)
ROUNDS_LIST = [6, 30, 50]  # Compare different round counts

results = {}

for rounds in ROUNDS_LIST:
    pci_values = []
    for rep in range(N):
        random.seed(rep * 1000 + rounds)
        # Run TTRL on ALL tasks (mixed modality, like Phase 1)
        w_final = train_phase_random(ALL_TASKS, init, rounds)
        pci = compute_pci(w_final)
        pci_values.append(pci)

    mu_pci = sum(pci_values) / len(pci_values)
    sd_pci = (sum((x - mu_pci) ** 2 for x in pci_values) / (len(pci_values) - 1)) ** 0.5
    se_pci = sd_pci / (len(pci_values) ** 0.5)
    ci_lo = mu_pci - 1.96 * se_pci
    ci_hi = mu_pci + 1.96 * se_pci

    results[rounds] = {
        "N": N,
        "mean_pci": round(mu_pci, 4),
        "sd_pci": round(sd_pci, 4),
        "se_pci": round(se_pci, 4),
        "ci_95_lo": round(ci_lo, 4),
        "ci_95_hi": round(ci_hi, 4),
        "min_pci": round(min(pci_values), 4),
        "max_pci": round(max(pci_values), 4),
    }
    print(f"\n=== Random Baseline (N={N}, rounds={rounds}) ===")
    print(f"  Mean PCI = {mu_pci:.4f} ± {se_pci:.4f}  (95% CI: [{ci_lo:.4f}, {ci_hi:.4f}])")
    print(f"  Range:    [{min(pci_values):.4f}, {max(pci_values):.4f}]")

# Also compute the theoretical expectation: for N→∞ rounds with random walk
# The weights don't converge to any point, they wander randomly
# But the EXPECTED distribution is still uniform
# So PCI(random, asymptotic) ≈ 0
print(f"\n=== Theoretical ===")
print(f"  PCI(uniform distribution) = 0.0000 (all weights equal)")
print(f"  PCI(random evaluator, infinite rounds) → 0.0000")

# Save
os.makedirs("experiments", exist_ok=True)
output = {
    "description": "Random evaluator baseline (shuffled judgments, 50/50 coin flip)",
    "notes": "Simulates TTRL where evaluator randomly picks winner. No real API calls.",
    "results": results,
    "theoretical_pci_uniform": 0.0,
}
with open("experiments/random_baseline.json", "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print("\nSaved: experiments/random_baseline.json")
