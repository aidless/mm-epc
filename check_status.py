import json, os, subprocess, random, math

cp = "C:/Users/Administrator/Desktop/aettl-research/experiments/multi_seed_ds_checkpoint.json"
log = "C:/Users/Administrator/Desktop/aettl-research/experiments/multi_seed_ds_run.log"

r = subprocess.run(["cmd","/c","tasklist","/FI","IMAGENAME eq python.exe","/FO","CSV"], capture_output=True, text=True, timeout=10)
n_py = len([l for l in r.stdout.split("\n") if "python.exe" in l])

if os.path.exists(cp):
    with open(cp) as f:
        c = json.load(f)
    n = c["last_rep"]
    results = c["results"]
    gtv = [x["gamma_TV"] for x in results]
    gvt = [x["gamma_VT"] for x in results]
    diffs = [x["gamma_VT"] - x["gamma_TV"] for x in results]
    m_tv = sum(gtv)/len(gtv)
    m_vt = sum(gvt)/len(gvt)
    m_diff = sum(diffs)/len(diffs)

    v_to_t = sum(1 for x in results if x["gamma_VT"] > x["gamma_TV"])
    t_to_v = sum(1 for x in results if x["gamma_TV"] > x["gamma_VT"])
    sym = sum(1 for x in results if x["gamma_TV"] == x["gamma_VT"])
    zeros = sum(1 for x in results if x["gamma_TV"]==0 and x["gamma_VT"]==0)

    print(f"Progress: {n}/30 ({n/30*100:.0f}%) | Python: {n_py}")
    print(f"g_TV={m_tv:.4f}  g_VT={m_vt:.4f}  diff={m_diff:.4f}")
    print(f"Dir: V->T={v_to_t} T->V={t_to_v} sym={sym} zeros={zeros}")

    for x in results[-3:]:
        rep = x["repetition"]
        gtv_val = x["gamma_TV"]
        gvt_val = x["gamma_VT"]
        print(f"  Rep {rep}: g_TV={gtv_val:.3f} g_VT={gvt_val:.3f}")

    avg_t = sum(x["time"] for x in results) / len(results)
    eta = (30-n) * avg_t / 60
    print(f"Avg/rep: {avg_t/60:.1f}min | ETA: {eta:.0f}min ({eta/60:.1f}h)")

    if n >= 30:
        print("*** COMPLETE! Computing stats... ***")
        se_diff = (sum((d-m_diff)**2 for d in diffs)/(n-1))**0.5 / (n**0.5)
        ci_lo = m_diff - 1.96*se_diff
        ci_hi = m_diff + 1.96*se_diff
        random.seed(42)
        bs_diffs = []
        for _ in range(10000):
            samp = [diffs[random.randint(0,n-1)] for _ in range(n)]
            bs_diffs.append(sum(samp)/n)
        p_two = sum(1 for d in bs_diffs if abs(d) >= abs(m_diff)) / 10000
        pooled_sd = ((sum((gtv[i]-m_tv)**2 for i in range(n)) + sum((gvt[i]-m_vt)**2 for i in range(n)))/(2*n-2))**0.5
        d_cohen = abs(m_diff) / max(0.001, pooled_sd)
        sig = "SIGNIFICANT p<.05" if p_two < 0.05 else "NOT SIG"
        print(f"95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
        print(f"p (bootstrap): {p_two:.4f}  {sig}")
        print(f"Cohen d: {d_cohen:.2f}")

elif os.path.exists(log):
    with open(log, encoding="utf-8", errors="replace") as f:
        content = f.read().replace(chr(0), "")
    phases = {}
    for ph in ["[T] done", "[V] done", "[TV] done", "[VT] done"]:
        phases[ph] = content.count(ph)
    print(f"No checkpoint. Python: {n_py}. Phases: {phases}")
else:
    print(f"No checkpoint or log. Python: {n_py}")
