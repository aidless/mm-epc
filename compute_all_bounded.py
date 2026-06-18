"""Compute JSD/Hellinger for ALL experiment datasets."""
import json, math, os

def jsd(p, q):
    m = {k: (p[k] + q[k]) / 2 for k in p}
    kl_pm = sum(p[k] * math.log(p[k]/m[k]) for k in p if p[k] > 0)
    kl_qm = sum(q[k] * math.log(q[k]/m[k]) for k in q if q[k] > 0)
    return (kl_pm + kl_qm) / 2

def hellinger(p, q):
    bc = sum(math.sqrt(p[k] * q[k]) for k in p)
    return math.sqrt(max(0, 1 - bc))

def analyze(path, label):
    if not os.path.exists(path): return None
    with open(path) as f: data = json.load(f)
    results = data.get("results", [])
    gtv = []; gvt = []; jsd_tv = []; jsd_vt = []; hel_tv = []; hel_vt = []
    for r in results:
        # Handle both old (gTV/gVT) and new (gamma_TV/gamma_VT) field names
        gtv.append(r.get("gamma_TV", r.get("gTV", 0)))
        gvt.append(r.get("gamma_VT", r.get("gVT", 0)))
        wT = r.get("w_T", {}); wV = r.get("w_V", {})
        wTV = r.get("w_TV", {}); wVT = r.get("w_VT", {})
        if wT and wTV and wV and wVT:
            jsd_tv.append(jsd(wV, wTV)); jsd_vt.append(jsd(wT, wVT))
            hel_tv.append(hellinger(wV, wTV)); hel_vt.append(hellinger(wT, wVT))
    n = len(jsd_tv)
    if n == 0: return None
    m_jsd_tv = sum(jsd_tv)/n; m_jsd_vt = sum(jsd_vt)/n
    m_hel_tv = sum(hel_tv)/n; m_hel_vt = sum(hel_vt)/n
    d_jsd = m_jsd_vt - m_jsd_tv; d_hel = m_hel_vt - m_hel_tv
    # Effect size for JSD difference
    diffs = [jsd_vt[i] - jsd_tv[i] for i in range(n)]
    sd_d = (sum((d-d_jsd)**2 for d in diffs)/(n-1))**0.5 if n > 1 else 0
    se_d = sd_d/(n**0.5) if n > 1 else 0
    # Bootstrap p
    import random; random.seed(42)
    bs = [sum([diffs[random.randint(0,n-1)] for _ in range(n)])/n for _ in range(10000)]
    p2 = sum(1 for d in bs if abs(d)>=abs(d_jsd))/10000
    # Pooled SD for Cohen's d
    pooled = ((sum((jsd_tv[i]-m_jsd_tv)**2 for i in range(n)) + sum((jsd_vt[i]-m_jsd_vt)**2 for i in range(n)))/(2*n-2))**0.5 if n > 1 else 0
    cohens = abs(d_jsd)/max(0.001,pooled)
    print(f"{label} (N={n}):")
    print(f"  JSD: T->V={m_jsd_tv:.4f} V->T={m_jsd_vt:.4f} diff={d_jsd:.4f} p={p2:.4f} d={cohens:.2f}")
    print(f"  Hellinger: T->V={m_hel_tv:.4f} V->T={m_hel_vt:.4f} diff={d_hel:.4f}")
    print(f"  gamma: T->V={sum(gtv)/len(gtv):.4f} V->T={sum(gvt)/len(gvt):.4f}")
    v2t = sum(1 for r in results if (r.get("gamma_VT",r.get("gVT",0)) > r.get("gamma_TV",r.get("gTV",0))))
    t2v = sum(1 for r in results if (r.get("gamma_TV",r.get("gTV",0)) > r.get("gamma_VT",r.get("gVT",0))))
    print(f"  Direction T->V: {t2v}/{n} JSD-dir: {'T->V' if d_jsd<0 else 'V->T'}")
    return {"label":label,"n":n,"jsd_tv":m_jsd_tv,"jsd_vt":m_jsd_vt,"jsd_diff":d_jsd,"jsd_p":p2,"jsd_d":cohens,"hel_tv":m_hel_tv,"hel_vt":m_hel_vt,"hel_diff":d_hel}

paths = [
    ("experiments/gpt4o_replication_checkpoint.json", "GPT-4o text"),
    ("experiments/real_image_checkpoint.json", "GPT-4o-mini real-img"),
    ("experiments/mm_epc_qwen_partial.json", "Qwen-plus"),
    ("experiments/multi_seed_ds_checkpoint.json", "DeepSeek self"),
]
print("="*60)
for p, label in paths:
    analyze(p, label)
