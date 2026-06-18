"""
MM-EPC Multi-Seed Statistical Validation
=========================================
N=30 independent repetitions of the 4-phase contagion experiment.
30 rounds per phase (120 rounds per repetition).
Total: 30 x 120 = 3,600 TTRL rounds -> ~10,800 API calls.

Setup: DeepSeek-chat (executor) x Qwen-plus (evaluator, via Bailian/DashScope)
This replaces the original GPT-4o evaluator (API2D ran out of credits).

Purpose: Tighten the bootstrap CI from Phase 3 (which was [-0.0002, 0.193])
to achieve statistical significance (p < 0.05).

Design decisions:
- 30 rounds (not 50): avoids the degeneration problem where step_by_step
  absorbs all weight mass at high round counts
- N=30 (not 10): gives enough statistical power (target > 0.8)
- Checkpoint after each repetition: crash recovery
"""

import json
import os
import re
import random
import time
import sys
import urllib.request
from copy import deepcopy
from datetime import datetime

# ============================================================
# API Keys
# ============================================================

DS_KEY = ""
BAILIAN_KEY = "sk-ab5c91f75f414e57ad5c04089a3ee0df"

# Read DeepSeek key from hermes .env (utf-8 encoding fixes the GBK decode error)
for p in [
    os.path.expanduser("~/AppData/Local/hermes/.env"),
    os.path.expanduser("~/.hermes/.env"),
    os.path.expanduser("~/.ccx/.env"),
]:
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'DEEPSEEK_API_KEY=(.+)', line)
                if m:
                    DS_KEY = m.group(1).strip().strip('"').strip("'")
                    break
        if DS_KEY:
            break
    except FileNotFoundError:
        continue

if not DS_KEY:
    print("ERROR: DEEPSEEK_API_KEY not found.")
    sys.exit(1)

print(f"[API] DS: {DS_KEY[:12]}... | Bailian: {BAILIAN_KEY[:12]}...")

# ============================================================
# API Helpers
# ============================================================

def ds_generate(system_prompt: str, user_prompt: str, temp: float = 0.7, mt: int = 400) -> str:
    """DeepSeek-chat: generates answers (executor role)."""
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt or " "},
            {"role": "user", "content": user_prompt or " "}
        ],
        "max_tokens": mt,
        "temperature": temp
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {DS_KEY}")
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    return resp["choices"][0]["message"]["content"]


def ds_evaluate(task: str, ans_a: str, ans_b: str, strat_a: str) -> str:
    """DeepSeek-chat as evaluator (self-evaluation mode).
    Returns 'A' if the strategy response wins, 'B' if step_by_step baseline wins."""
    up = (
        f"Evaluate which response is better for the given task.\n"
        f"Task: {task}\n\n"
        f"A ({strat_a}): {ans_a[:300]}\n\n"
        f"B (step_by_step): {ans_b[:300]}\n\n"
        f"Output only A or B."
    )
    body = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": up}],
        "max_tokens": 5,
        "temperature": 0
    }).encode()
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=body, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {DS_KEY}")
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    txt = resp["choices"][0]["message"]["content"].strip().upper()
    if "A" in txt:
        return "A"
    elif "B" in txt:
        return "B"
    else:
        return "A" if txt.startswith("A") else "B"


# ============================================================
# Data
# ============================================================

STRATEGIES = {
    "step_by_step": "逐步推理",
    "critical_check": "先答再审",
    "first_principles": "基本原理",
    "creative_leap": "创新方案",
    "analogy_meta": "类比举例",
    "evidence_cite": "引用依据",
    "synthesis": "综合视角",
    "counterfactual": "反例边界",
    "visual_grounding": "先构建视觉画面再推理",
    "spatial_decompose": "空间/几何组件分解",
    "aesthetic_frame": "美学框架系统评估",
}

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


# ============================================================
# Core Algorithm
# ============================================================

def train_phase(
    name: str,
    task_list: list,
    initial_weights: dict,
    rounds: int,
    seed: int,
) -> dict:
    """Run TTRL on a task list, return final weights."""
    random.seed(seed)
    w = deepcopy(initial_weights)
    n_tasks = len(task_list)

    wins = 0
    for i in range(rounds):
        tk = task_list[i % n_tasks]

        # Sample strategy from weight distribution (roulette wheel)
        rv = random.random() * sum(w.values())
        cum = 0.0
        st = "step_by_step"
        for k, v in w.items():
            cum += v
            if rv <= cum:
                st = k
                break

        # Retry loop for API failures
        for attempt in range(3):
            try:
                # Generate responses
                o = ds_generate(f"你是专家。策略：{STRATEGIES[st]}", tk["q"])
                c = ds_generate("你是专家。策略：逐步推理。", tk["q"])
                # Evaluate
                wn = ds_evaluate(tk["q"], o, c, st)

                # Update weights
                upd = 0.08 if wn == "A" else -0.04
                if wn == "A":
                    wins += 1
                w[st] = max(0.001, w[st] + upd)
                tot = max(0.01, sum(w.values()))
                w = {k: max(0.001, v / tot) for k, v in w.items()}
                tot = sum(w.values())
                w = {k: v / tot for k, v in w.items()}
                time.sleep(0.1)
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    print(f"  [{name}] r{i} FAIL: {e}", flush=True)

    top_s = max(w, key=w.get)
    pci = compute_pci(w)
    print(f"  [{name}] done: top={top_s}({w[top_s]:.0%}) wins={wins}/{rounds} PCI={pci:.3f}", flush=True)
    return w


def contagion(w_pure: dict, w_contaminated: dict) -> float:
    """gamma = ||w_contaminated - w_pure||_2 / ||w_pure||_2"""
    pure_vec = list(w_pure.values())
    cont_vec = list(w_contaminated.values())
    diff = sum((a - b) ** 2 for a, b in zip(pure_vec, cont_vec)) ** 0.5
    norm = sum(v ** 2 for v in pure_vec) ** 0.5
    return round(diff / max(0.001, norm), 4)


def compute_pci(weights: dict) -> float:
    """PCI = sigma(w) / mu(w)"""
    vals = list(weights.values())
    mu = sum(vals) / len(vals)
    if mu < 1e-10:
        return 0.0
    sigma = (sum((v - mu) ** 2 for v in vals) / len(vals)) ** 0.5
    return sigma / mu


def run_one_repetition(rep: int, rounds: int) -> dict:
    """Run complete 4-phase contagion experiment once."""
    seed_base = rep * 10000 + rounds
    init = {k: 1.0 / len(STRATEGIES) for k in STRATEGIES}

    t0 = time.time()

    # Phase A: Pure text training
    w_T = train_phase("T", TEXT_TASKS, init, rounds, seed_base + 1)

    # Phase B: Pure visual training
    w_V = train_phase("V", VISUAL_TASKS, init, rounds, seed_base + 2)

    # Phase C: Contagion T -> V (text weights, visual tasks)
    w_TV = train_phase("TV", VISUAL_TASKS, w_T, rounds, seed_base + 3)

    # Phase D: Contagion V -> T (visual weights, text tasks)
    w_VT = train_phase("VT", TEXT_TASKS, w_V, rounds, seed_base + 4)

    elapsed = time.time() - t0

    gamma_TV = contagion(w_V, w_TV)
    gamma_VT = contagion(w_T, w_VT)
    asymmetry = round(
        abs(gamma_TV - gamma_VT) / max(0.001, gamma_TV + gamma_VT), 4
    )

    # Compute PCI for each phase
    pci_T = compute_pci(w_T)
    pci_V = compute_pci(w_V)
    pci_TV = compute_pci(w_TV)
    pci_VT = compute_pci(w_VT)

    return {
        "repetition": rep,
        "rounds": rounds,
        "gamma_TV": gamma_TV,
        "gamma_VT": gamma_VT,
        "asymmetry": asymmetry,
        "asymmetric": gamma_TV != gamma_VT,
        "direction": (
            "T->V" if gamma_TV > gamma_VT
            else ("V->T" if gamma_VT > gamma_TV else "symmetric")
        ),
        "w_T_top": max(w_T, key=w_T.get),
        "w_V_top": max(w_V, key=w_V.get),
        "w_TV_top": max(w_TV, key=w_TV.get),
        "w_VT_top": max(w_VT, key=w_VT.get),
        "pci_T": round(pci_T, 4),
        "pci_V": round(pci_V, 4),
        "pci_TV": round(pci_TV, 4),
        "pci_VT": round(pci_VT, 4),
        "w_T": {k: round(v, 3) for k, v in sorted(w_T.items(), key=lambda x: -x[1])},
        "w_V": {k: round(v, 3) for k, v in sorted(w_V.items(), key=lambda x: -x[1])},
        "w_TV": {k: round(v, 3) for k, v in sorted(w_TV.items(), key=lambda x: -x[1])},
        "w_VT": {k: round(v, 3) for k, v in sorted(w_VT.items(), key=lambda x: -x[1])},
        "time": elapsed,
    }


# ============================================================
# Statistics
# ============================================================

def compute_statistics(results: list, n_bootstrap: int = 10000) -> dict:
    """Compute comprehensive statistics from N repetitions."""
    g_TV = [r["gamma_TV"] for r in results]
    g_VT = [r["gamma_VT"] for r in results]
    asyms = [r["asymmetry"] for r in results]
    diffs = [r["gamma_VT"] - r["gamma_TV"] for r in results]
    n = len(g_TV)

    # Means
    mean_TV = sum(g_TV) / n
    mean_VT = sum(g_VT) / n
    mean_diff = sum(diffs) / n

    # Standard error of the difference
    sd_diff = (sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)) ** 0.5
    se_diff = sd_diff / (n ** 0.5)

    # 95% CI
    ci_lo = mean_diff - 1.96 * se_diff
    ci_hi = mean_diff + 1.96 * se_diff

    # Paired t-test
    t_stat = mean_diff / (sd_diff / (n ** 0.5)) if sd_diff > 0 else 0.0

    # Bootstrap p-value
    random.seed(42)
    bootstrap_diffs = []
    for _ in range(n_bootstrap):
        sample = [diffs[random.randint(0, n - 1)] for _ in range(n)]
        bootstrap_diffs.append(sum(sample) / n)
    p_bootstrap_one = sum(1 for d in bootstrap_diffs if d <= 0) / n_bootstrap
    p_bootstrap_two = sum(
        1 for d in bootstrap_diffs if abs(d) >= abs(mean_diff)
    ) / n_bootstrap

    # Cohen's d
    pooled_sd = (
        (sum((g_TV[i] - mean_TV) ** 2 for i in range(n)) +
         sum((g_VT[i] - mean_VT) ** 2 for i in range(n))) / (2 * n - 2)
    ) ** 0.5
    cohens_d = abs(mean_diff) / max(0.001, pooled_sd)

    # Effect size
    if cohens_d < 0.2:
        effect = "negligible"
    elif cohens_d < 0.5:
        effect = "small"
    elif cohens_d < 0.8:
        effect = "medium"
    else:
        effect = "large"

    # Counts
    n_asymmetric = sum(1 for r in results if r["asymmetric"])
    n_zero = sum(
        1 for r in results if r["gamma_TV"] == 0.0 and r["gamma_VT"] == 0.0
    )

    # Direction consistency (computed from gamma values, not stored direction field)
    v_to_t_count = sum(1 for r in results if r["gamma_VT"] > r["gamma_TV"])
    t_to_v_count = sum(1 for r in results if r["gamma_TV"] > r["gamma_VT"])
    symmetric_count = sum(1 for r in results if r["gamma_TV"] == r["gamma_VT"])
    if v_to_t_count > t_to_v_count:
        dominant_dir = "V->T"
    elif t_to_v_count > v_to_t_count:
        dominant_dir = "T->V"
    else:
        dominant_dir = "symmetric"

    return {
        "N": n,
        "n_bootstrap": n_bootstrap,
        "mean_gamma_TV": round(mean_TV, 4),
        "mean_gamma_VT": round(mean_VT, 4),
        "mean_difference": round(mean_diff, 4),
        "se_difference": round(se_diff, 4),
        "sd_difference": round(sd_diff, 4),
        "ci_95": [round(ci_lo, 4), round(ci_hi, 4)],
        "ci_width": round(ci_hi - ci_lo, 4),
        "t_statistic": round(t_stat, 4),
        "df": n - 1,
        "p_bootstrap_one_sided": round(p_bootstrap_one, 4),
        "p_bootstrap_two_sided": round(p_bootstrap_two, 4),
        "significant_at_0_05": p_bootstrap_two < 0.05,
        "significant_at_0_01": p_bootstrap_two < 0.01,
        "cohens_d": round(cohens_d, 4),
        "effect_size": effect,
        "n_asymmetric": n_asymmetric,
        "n_zero_contagion": n_zero,
        "asymmetry_rate": round(n_asymmetric / max(1, n), 3),
        "zero_rate": round(n_zero / max(1, n), 3),
        "dominant_direction": dominant_dir,
    }


# ============================================================
# Main
# ============================================================

def main():
    N = 30
    ROUNDS = 30

    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiments")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "multi_seed_ds_checkpoint.json")
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, "mm_epc_multi_seed_ds_final.json")
    LOG_PATH = os.path.join(OUTPUT_DIR, "multi_seed_ds_run.log")

    # Redirect stdout to log file (unbuffered)
    sys.stdout = open(LOG_PATH, "w", encoding="utf-8", buffering=1)

    # Resume from checkpoint
    results = []
    start_rep = 1
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, encoding="utf-8") as f:
                checkpoint = json.load(f)
                results = checkpoint.get("results", [])
                start_rep = len(results) + 1
                if results:
                    print(f"[RESUME] {len(results)}/{N} done, starting at rep {start_rep}")
        except Exception:
            print("[RESUME] Checkpoint corrupted, starting fresh")

    total_rounds = N * 4 * ROUNDS
    total_calls = total_rounds * 3  # 2 DS gen + 1 Qwen eval per round

    print(f"""
{'='*60}
  MM-EPC Multi-Seed Validation
  N={N}, Rounds/phase={ROUNDS}, Total rounds={total_rounds}
  Executor: DeepSeek-chat | Evaluator: DeepSeek-chat (self-eval)
  ~{total_calls:,} API calls | Est. ~{total_rounds * 5 / 3600:.1f}h
{'='*60}
""")

    t_start = time.time()

    for rep in range(start_rep, N + 1):
        n_done = rep - start_rep + 1
        print(f"\n--- Rep {rep}/{N} (#{n_done} this session) ---", flush=True)

        try:
            result = run_one_repetition(rep, ROUNDS)
            results.append(result)

            elapsed_rep = result["time"]
            elapsed_total = time.time() - t_start
            avg_per_rep = elapsed_total / n_done
            eta_min = avg_per_rep * (N - rep) / 60

            print(f"  g_TV={result['gamma_TV']} g_VT={result['gamma_VT']} "
                  f"asym={result['asymmetry']} dir={result['direction']}")
            print(f"  PCI: T={result['pci_T']} V={result['pci_V']} "
                  f"TV={result['pci_TV']} VT={result['pci_VT']}")
            print(f"  Top: T={result['w_T_top']} V={result['w_V_top']} "
                  f"TV={result['w_TV_top']} VT={result['w_VT_top']}")
            print(f"  [{elapsed_rep:.0f}s] ETA: {eta_min:.0f}min | "
                  f"Elapsed: {elapsed_total/60:.0f}min", flush=True)

        except Exception as e:
            print(f"  ERROR rep {rep}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "results": results, "last_rep": rep - 1,
                    "error": str(e),
                }, f, indent=2, ensure_ascii=False)
            print("  Checkpoint saved. Exiting.", flush=True)
            sys.exit(1)

        # Save checkpoint
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump({"results": results, "last_rep": rep},
                      f, indent=2, ensure_ascii=False)

    # ================================================
    # Final statistics
    # ================================================
    print(f"\n{'='*60}")
    print("Computing final statistics (10,000 bootstrap resamples)...")
    print(f"{'='*60}", flush=True)

    stats = compute_statistics(results)
    total_time = time.time() - t_start

    output = {
        "experiment": "MM-EPC Multi-Seed Statistical Validation",
        "timestamp": datetime.now().isoformat(),
        "setup": {
            "executor": "deepseek-chat",
            "evaluator": "deepseek-chat (self-evaluation)",
            "evaluator_endpoint": "https://api.deepseek.com/chat/completions",
        },
        "parameters": {
            "N_repetitions": N,
            "rounds_per_phase": ROUNDS,
            "phases": ["pure_text", "pure_visual", "contagion_TV", "contagion_VT"],
            "alpha_win": 0.08,
            "alpha_lose": -0.04,
            "n_strategies": len(STRATEGIES),
            "n_text_tasks": len(TEXT_TASKS),
            "n_visual_tasks": len(VISUAL_TASKS),
        },
        "results": results,
        "statistics": stats,
        "total_time_seconds": round(total_time, 1),
        "total_api_calls_approx": total_calls,
        "total_ttrl_rounds": total_rounds,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Report
    sig_05 = "YES" if stats["significant_at_0_05"] else "NO"
    sig_01 = "YES" if stats["significant_at_0_01"] else "NO"
    emoji_05 = "!!!" if stats["significant_at_0_05"] else "--"
    emoji_01 = "!!!" if stats["significant_at_0_01"] else "--"

    print(f"""
{'='*60}
         MM-EPC MULTI-SEED FINAL REPORT
{'='*60}
N = {N} reps x {ROUNDS} rounds x 4 phases = {total_rounds} rounds
~{total_calls:,} API calls | {total_time/60:.0f} min ({total_time/3600:.1f}h)

Contagion Coefficients (mean +/- SE):
  gamma_T>V = {stats['mean_gamma_TV']}
  gamma_V>T = {stats['mean_gamma_VT']}
  Difference = {stats['mean_difference']} +/- {stats['se_difference']}
  95% CI:    [{stats['ci_95'][0]}, {stats['ci_95'][1]}]

Statistical Tests:
  t({stats['df']}) = {stats['t_statistic']}
  p (bootstrap, two-sided) = {stats['p_bootstrap_two_sided']}
  Cohen's d = {stats['cohens_d']} ({stats['effect_size']})
  Significant at 0.05: {sig_05} {emoji_05}
  Significant at 0.01: {sig_01} {emoji_01}

Asymmetry detected: {stats['n_asymmetric']}/{N} reps ({stats['asymmetry_rate']:.0%})
Zero contagion:     {stats['n_zero_contagion']}/{N} reps ({stats['zero_rate']:.0%})
Dominant direction: {stats['dominant_direction']}

Saved: {OUTPUT_FILE}
{'='*60}
""")

    return output


if __name__ == "__main__":
    main()
