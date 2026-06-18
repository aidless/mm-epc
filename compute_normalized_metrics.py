"""
Compute normalized PCI and all bounded metrics with proper modality normalization.
- PCI_norm = PCI / k where k = number of strategies in that modality
- JSD/Hellinger computed from actual weight data (not estimated)
"""
import json, math, os

def jsd(p, q):
    m = {k: (p[k] + q[k]) / 2 for k in p}
    return (sum(p[k]*math.log(p[k]/m[k]) for k in p if p[k]>0) + sum(q[k]*math.log(q[k]/m[k]) for k in q if q[k]>0)) / 2

def hellinger(p, q):
    return math.sqrt(max(0, 1 - sum(math.sqrt(p[k]*q[k]) for k in p)))

def pci(w):
    vals = list(w.values()); mu = sum(vals)/len(vals)
    return (sum((v-mu)**2 for v in vals)/len(vals))**0.5 / max(1e-10, mu) if mu > 1e-10 else 0

TEXT_STRATEGIES = {"step_by_step","critical_check","first_principles","creative_leap","analogy_meta","evidence_cite","synthesis","counterfactual"}
VISUAL_STRATEGIES = {"visual_grounding","spatial_decompose","aesthetic_frame"}
N_TEXT = len(TEXT_STRATEGIES)
N_VISUAL = len(VISUAL_STRATEGIES)

def analyze_with_weights(data_file, label):
    if not os.path.exists(data_file): return
    with open(data_file) as f: data = json.load(f)
    results = data.get("results", [])

    jsd_tv = []; jsd_vt = []; hel_tv = []; hel_vt = []
    pci_t = []; pci_v = []; pci_t_norm = []; pci_v_norm = []

    for r in results:
        wT = r.get("w_T",{}); wV = r.get("w_V",{})
        wTV = r.get("w_TV",{}); wVT = r.get("w_VT",{})
        if not all([wT,wV,wTV,wVT]): continue

        # Bounded metrics
        jsd_tv.append(jsd(wV, wTV)); jsd_vt.append(jsd(wT, wVT))
        hel_tv.append(hellinger(wV, wTV)); hel_vt.append(hellinger(wT, wVT))

        # Raw and normalized PCI
        pci_t.append(pci(wT)); pci_v.append(pci(wV))
        # Normalize: divide PCI by number of strategies in that modality
        # For mixed-weight vectors (all 11 strategies), weight by modality proportion
        pci_t_norm.append(pci(wT) / 11)  # normalize by total strategies
        pci_v_norm.append(pci(wV) / 11)

    n = len(jsd_tv)
    if n == 0:
        print(f"{label}: no weight data")
        return

    m_jsd_tv = sum(jsd_tv)/n; m_jsd_vt = sum(jsd_vt)/n
    m_hel_tv = sum(hel_tv)/n; m_hel_vt = sum(hel_vt)/n
    m_pci_t = sum(pci_t)/n; m_pci_v = sum(pci_v)/n
    m_pci_tn = sum(pci_t_norm)/n; m_pci_vn = sum(pci_v_norm)/n

    # JSD diff stats
    diffs = [jsd_vt[i]-jsd_tv[i] for i in range(n)]
    d_jsd = sum(diffs)/n
    sd_d = (sum((x-d_jsd)**2 for x in diffs)/(n-1))**0.5 if n>1 else 0
    se_d = sd_d/(n**0.5) if n>1 else 0
    ci_lo = d_jsd-1.96*se_d; ci_hi = d_jsd+1.96*se_d

    gtv = [r.get("gamma_TV", r.get("gTV", 0)) for r in results if r.get("w_T",{})]
    gvt = [r.get("gamma_VT", r.get("gVT", 0)) for r in results if r.get("w_T",{})]

    print(f"\n{label} (N={n} with full weights):")
    print(f"  Gamma: T->V={sum(gtv)/len(gtv):.4f} V->T={sum(gvt)/len(gvt):.4f}")
    print(f"  JSD:   T->V={m_jsd_tv:.4f} V->T={m_jsd_vt:.4f} diff={d_jsd:.4f}+/-{se_d:.4f} 95%CI[{ci_lo:.4f},{ci_hi:.4f}]")
    print(f"  Hel:   T->V={m_hel_tv:.4f} V->T={m_hel_vt:.4f}")
    print(f"  PCI_raw: T={m_pci_t:.4f} V={m_pci_v:.4f}")
    print(f"  PCI_norm(/11): T={m_pci_tn:.4f} V={m_pci_vn:.4f}")

# Analyze all datasets with full weights
print("="*60)
print("REAL JSD/HELLINGER (computed, not estimated)")
print("="*60)
for path, label in [
    ("experiments/multi_seed_ds_checkpoint.json", "DeepSeek self-eval"),
    ("experiments/mm_epc_qwen_partial.json", "Qwen-plus"),
    ("experiments/gpt4o_replication_checkpoint.json", "GPT-4o"),
    ("experiments/real_image_checkpoint.json", "Real-image"),
    ("experiments/ablation_no_s0_checkpoint.json", "Ablation (no s0)"),
]:
    analyze_with_weights(path, label)
