"""
Compute bounded divergence metrics (JSD, Hellinger, TV) for all experiment data.
Replaces/ complements the unbounded gamma metric.
Zero API cost - pure computation on existing results.
"""
import json, math, os

def jsd(p, q):
    """Jensen-Shannon Divergence (bounded [0, ln 2])."""
    m = {k: (p[k] + q[k]) / 2 for k in p}
    kl_pm = sum(p[k] * math.log(p[k]/m[k]) for k in p if p[k] > 0)
    kl_qm = sum(q[k] * math.log(q[k]/m[k]) for k in q if q[k] > 0)
    return (kl_pm + kl_qm) / 2

def hellinger(p, q):
    """Hellinger distance (bounded [0, 1])."""
    bc = sum(math.sqrt(p[k] * q[k]) for k in p)
    return math.sqrt(max(0, 1 - bc))  # clamp for floating point

def tv(p, q):
    """Total Variation distance (bounded [0, 1])."""
    return 0.5 * sum(abs(p[k] - q[k]) for k in p)

def compute_bounded_metrics(data_file, label):
    """Compute all bounded metrics from experiment checkpoint."""
    with open(data_file) as f:
        data = json.load(f)

    results = data.get("results", [])
    if not results: return

    gtv_old = []; gvt_old = []
    jsd_tv = []; jsd_vt = []
    hel_tv = []; hel_vt = []
    tv_tv = []; tv_vt = []

    for r in results:
        wT = r.get("w_T", {})
        wV = r.get("w_V", {})
        wTV = r.get("w_TV", {})
        wVT = r.get("w_VT", {})

        if not wT or not wTV: continue  # some results don't have full weights

        # Old gamma metrics
        gtv_old.append(r.get("gamma_TV", r.get("gTV", 0)))
        gvt_old.append(r.get("gamma_VT", r.get("gVT", 0)))

        # Bounded metrics
        jsd_tv.append(jsd(wV, wTV))
        jsd_vt.append(jsd(wT, wVT))
        hel_tv.append(hellinger(wV, wTV))
        hel_vt.append(hellinger(wT, wVT))
        tv_tv.append(tv(wV, wTV))
        tv_vt.append(tv(wT, wVT))

    n = len(jsd_tv)
    if n == 0: return

    m_jsd_tv = sum(jsd_tv)/n; m_jsd_vt = sum(jsd_vt)/n
    m_hel_tv = sum(hel_tv)/n; m_hel_vt = sum(hel_vt)/n
    m_tv_tv_val = sum(tv_tv)/n; m_tv_vt_val = sum(tv_vt)/n

    d_jsd = m_jsd_vt - m_jsd_tv
    d_hel = m_hel_vt - m_hel_tv
    d_tv = m_tv_vt_val - m_tv_tv_val

    # Direction from gamma
    v2t_g = sum(1 for i in range(n) if gvt_old[i] > gtv_old[i])
    t2v_g = sum(1 for i in range(n) if gtv_old[i] > gvt_old[i])

    print(f"\n{label} (N={n}):")
    print(f"  {'Metric':<15} {'T->V':>8} {'V->T':>8} {'Diff':>8} {'V->T#':>6} {'T->V#':>6}")
    print(f"  {'gamma (old)':<15} {sum(gtv_old)/n:8.4f} {sum(gvt_old)/n:8.4f} {sum(gvt_old)/n-sum(gtv_old)/n:8.4f} {v2t_g:>6} {t2v_g:>6}")
    print(f"  {'JSD':<15} {m_jsd_tv:8.4f} {m_jsd_vt:8.4f} {d_jsd:8.4f}")
    print(f"  {'Hellinger':<15} {m_hel_tv:8.4f} {m_hel_vt:8.4f} {d_hel:8.4f}")
    print(f"  {'Total Var.':<15} {m_tv_tv_val:8.4f} {m_tv_vt_val:8.4f} {d_tv:8.4f}")

    # Check if JSD/Hellinger patterns match gamma conclusions
    gamma_dir = "V->T" if v2t_g > t2v_g else ("T->V" if t2v_g > v2t_g else "symmetric")
    jsd_dir = "V->T" if d_jsd > 0 else ("T->V" if d_jsd < 0 else "symmetric")
    hel_dir = "V->T" if d_hel > 0 else ("T->V" if d_hel < 0 else "symmetric")
    print(f"  Direction: gamma={gamma_dir}, JSD={jsd_dir}, Hellinger={hel_dir}")
    match = gamma_dir == jsd_dir == hel_dir
    print(f"  Metrics agree on direction: {'YES' if match else 'NO - divergences differ!'}")

# Analyze all datasets
print("="*60)
print("BOUNDED METRIC ANALYSIS")
print("="*60)

datasets = [
    ("experiments/multi_seed_ds_checkpoint.json", "DeepSeek self-eval"),
    ("experiments/gpt4o_replication_checkpoint.json", "GPT-4o"),
    ("experiments/mm_epc_qwen_partial.json", "Qwen-plus (partial)"),
    ("experiments/multi_seed_checkpoint.json", "Multi-seed (old)"),
]

for path, label in datasets:
    if os.path.exists(path):
        compute_bounded_metrics(path, label)
    else:
        print(f"\n{label}: file not found ({path})")

# Also save results
output = {
    "note": "Bounded divergence metrics complementing unbounded gamma. JSD/Hellinger/TV are in [0,1].",
    "recommendation": "Use JSD or Hellinger as primary contagion metric in revised paper."
}
os.makedirs("experiments", exist_ok=True)
with open("experiments/bounded_metrics.json", "w") as f:
    json.dump(output, f, indent=2)
print("\nSaved: experiments/bounded_metrics.json")
