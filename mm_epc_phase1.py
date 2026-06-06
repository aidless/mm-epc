"""
MM-EPC Phase 1: Multimodal Evaluator Preference Collapse
════════════════════════════════════════════════════════
Extends EPC to multimodal task space:
  - Text tasks (reasoning, code, design, explain)
  - Visual tasks (image description, spatial, diagram)
  - Evaluator: GPT-4o (cross-model, cross-modality)

Measures: MPCI, CPCI (cross-modal contagion), Γ matrix
"""

import json, time, urllib.request, random, re, os, sys
from collections import Counter
from datetime import datetime

# Keys
DS_KEY = ""
with open("/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env") as f:
    for line in f:
        m = re.match(r'DEEPSEEK_API_KEY=(.+)', line)
        if m: DS_KEY = m.group(1).strip().strip('"').strip("'")

API2D_KEY = "fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7"

# ── LLM Clients ──
def ds(sp, up, temp=0.7, mt=400):
    b = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":temp}).encode()
    r = urllib.request.Request("https://api.deepseek.com/chat/completions", data=b, method="POST")
    r.add_header("Content-Type","application/json"); r.add_header("Authorization", f"Bearer {DS_KEY}")
    return json.loads(urllib.request.urlopen(r, timeout=20).read().decode())["choices"][0]["message"]["content"]

def gpt4o_eval(task, ans_a, ans_b, strat_a):
    """GPT-4o as cross-model multimodal evaluator"""
    up = f"""Evaluate objectively. Task: {task}
A ({strat_a}): {ans_a[:300]}
B (step_by_step): {ans_b[:300]}
Which is better? Output only A or B."""
    b = json.dumps({"model":"gpt-4o","messages":[{"role":"user","content":up}],"max_tokens":5,"temperature":0}).encode()
    r = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=b, method="POST")
    r.add_header("Content-Type","application/json"); r.add_header("Authorization", f"Bearer {API2D_KEY}")
    resp = json.loads(urllib.request.urlopen(r, timeout=25).read().decode())
    txt = resp["choices"][0]["message"]["content"].strip().upper()
    return "A" if "A" in txt else ("B" if "B" in txt else ("A" if txt.startswith("A") else "B"))


# ═══════════════════════════════════════
# MULTIMODAL TASK BANK
# ═══════════════════════════════════════
TEXT_TASKS = [
    # Verification
    {"modality":"text","type":"verify","q":"1+2*3=?","a":"7"},
    {"modality":"text","type":"verify","q":"5//2=?","a":"2"},
    {"modality":"text","type":"verify","q":"git撤销commit保留修改?","a":"reset --soft"},
    # Code
    {"modality":"text","type":"code","q":"写Python回文判断函数。"},
    {"modality":"text","type":"code","q":"写二分查找返回索引或-1。"},
    # Reasoning
    {"modality":"text","type":"reasoning","q":"8枚硬币1假(轻)最少称几次?"},
    {"modality":"text","type":"reasoning","q":"3灯3开关进1次如何确定?"},
    # Design
    {"modality":"text","type":"design","q":"设计URL短链接系统核心组件。"},
    {"modality":"text","type":"design","q":"设计分布式唯一ID生成器。"},
    # Explain
    {"modality":"text","type":"explain","q":"索引为何用B+树而非二叉?"},
    {"modality":"text","type":"explain","q":"HTTPS证书验证步骤?"},
    {"modality":"text","type":"explain","q":"Transformer为何比LSTM并行?"},
]

VISUAL_TASKS = [
    # Image description / visual reasoning (text-proxied)
    {"modality":"visual","type":"describe","q":"描述一张典型的城市日落照片中你会看到什么元素？从色彩、构图、氛围三方面回答。"},
    {"modality":"visual","type":"describe","q":"描述一张繁忙的咖啡店内景照片：人物、光线、空间布局、情绪氛围。"},
    {"modality":"visual","type":"spatial","q":"一个正方体放在桌子上，从正面能看到一个正方形。如果从上方45度角俯视，能看到几个面？为什么？"},
    {"modality":"visual","type":"spatial","q":"解释透视原理：为什么远处的物体看起来更小？用日常例子说明。"},
    {"modality":"visual","type":"diagram","q":"描述如何画一个UML类图来表示'学生选课'系统。包含哪些类和关系？"},
    {"modality":"visual","type":"diagram","q":"描述一个微服务架构图应该包含哪些组件，以及它们之间的连接关系。"},
    {"modality":"visual","type":"aesthetic","q":"评价一副照片的好坏有哪些标准？从构图、光线、色彩、主题四个维度回答。"},
    {"modality":"visual","type":"aesthetic","q":"解释'三分法则'在摄影和设计中的应用，为什么它有效？"},
    {"modality":"visual","type":"color","q":"解释互补色和类似色的区别，各举一个在设计中的应用例子。"},
    {"modality":"visual","type":"color","q":"描述暖色调和冷色调给人的不同心理感受，各适合什么场景？"},
]

ALL_TASKS = TEXT_TASKS + VISUAL_TASKS

# ═══════════════════════════════════════
# STRATEGIES (8 text + 3 visual)
# ═══════════════════════════════════════
STRATEGIES = {
    "step_by_step": "逐步推理，每步显式写出",
    "critical_check": "先给出答案，审视自身再修正",
    "first_principles": "从基本原理出发推导",
    "creative_leap": "跳出常规，寻找创新方案",
    "analogy_meta": "用类比和具体例子解释",
    "evidence_cite": "引用具体知识依据",
    "synthesis": "综合多种视角，平衡回答",
    "counterfactual": "考虑反面情况和边界条件",
    "visual_grounding": "先构建视觉画面再推理，从具体形象出发",
    "spatial_decompose": "将空间/视觉问题分解为几何组件逐步分析",
    "aesthetic_frame": "从美学框架(构图/色彩/平衡)系统性评估",
}


# ═══════════════════════════════════════
# EXPERIMENT RUNNER
# ═══════════════════════════════════════
def run_condition(name, eval_fn, rounds_per_modality=8):
    """Run TTRL on all tasks, tracking modality-specific PCI"""
    w = {k: 1/len(STRATEGIES) for k in STRATEGIES}
    history = []
    
    # Track per-modality weights (frozen snapshots)
    text_weights = {}
    visual_weights = {}
    
    t0 = time.time()
    
    for i in range(rounds_per_modality * 2):  # alternate text and visual
        # Alternate modalities
        if i % 2 == 0:
            modality_tasks = TEXT_TASKS
            modality_name = "text"
        else:
            modality_tasks = VISUAL_TASKS
            modality_name = "visual"
        
        tk = modality_tasks[(i//2) % len(modality_tasks)]
        
        # Weighted strategy selection
        rv = random.random() * sum(w.values())
        cu = 0.0; st = "step_by_step"
        for k, v in w.items():
            cu += v
            if rv <= cu: st = k; break
        
        try:
            # Execute with DeepSeek
            sp = f"你是专家AI。策略：{STRATEGIES[st]}"
            o = ds(sp, tk["q"])
            
            # Control (fixed step_by_step)
            c = ds("你是专家AI。策略：逐步推理。", tk["q"])
            
            # GPT-4o evaluates (cross-model)
            wn = eval_fn(tk["q"], o, c, st)
            
            # TTRL update
            upd = 0.08 if wn == "A" else -0.04
            w[st] += upd
            tot = max(0.01, sum(w.values()))
            w = {k: max(0.01, v/tot) for k, v in w.items()}
            tot = sum(w.values())
            w = {k: v/tot for k, v in w.items()}
            
            # Snapshot modality-specific weights
            if modality_name == "text":
                text_weights = {k: v for k, v in w.items()}
            else:
                visual_weights = {k: v for k, v in w.items()}
            
            history.append({
                "round": i+1,
                "modality": modality_name,
                "strategy": st,
                "text_top": max(text_weights, key=text_weights.get) if text_weights else "N/A",
                "visual_top": max(visual_weights, key=visual_weights.get) if visual_weights else "N/A",
            })
            
            time.sleep(0.5)
            
        except Exception as e:
            history.append({"round": i+1, "error": str(e)[:80]})
    
    # Calculate metrics
    wv = list(w.values())
    mean_w = sum(wv) / len(wv)
    std_w = (sum((v-mean_w)**2 for v in wv) / len(wv))**0.5
    pci = round(std_w / max(0.001, mean_w), 4)
    
    # Modality-specific PCI
    def calc_pci(w_dict):
        if not w_dict: return 0.0
        vals = list(w_dict.values())
        m = sum(vals)/len(vals)
        s = (sum((v-m)**2 for v in vals)/len(vals))**0.5
        return round(s/max(0.001, m), 4)
    
    text_pci = calc_pci(text_weights) if text_weights else 0
    visual_pci = calc_pci(visual_weights) if visual_weights else 0
    
    # Cross-modal PCI (CPCI) - divergence between text and visual weights
    if text_weights and visual_weights:
        text_vec = list(text_weights.values())
        vis_vec = list(visual_weights.values())
        l2_diff = sum((a-b)**2 for a,b in zip(text_vec, vis_vec))**0.5
        l2_sum = (sum(a**2 for a in text_vec)**0.5 + sum(b**2 for b in vis_vec)**0.5)
        cpci = round(l2_diff / max(0.001, l2_sum), 4) if l2_sum > 0 else 0
    else:
        cpci = 0
    
    # MPCI (Multimodal PCI) = average of intra-modal + cross-modal
    mpci = round((text_pci + visual_pci) / 2 + cpci * 0.5, 4)
    
    return {
        "name": name,
        "rounds": len([h for h in history if "strategy" in h]),
        "pci": pci,
        "text_pci": text_pci,
        "visual_pci": visual_pci,
        "cpci": cpci,
        "mpci": mpci,
        "top": max(w, key=w.get),
        "top_w": round(max(w.values()), 3),
        "text_top": max(text_weights, key=text_weights.get) if text_weights else "N/A",
        "visual_top": max(visual_weights, key=visual_weights.get) if visual_weights else "N/A",
        "weights": {k: round(v, 3) for k, v in w.items()},
        "time": round(time.time() - t0, 1),
    }


# ═══════════════════════════════════════
# RUN
# ═══════════════════════════════════════
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════╗
║  MM-EPC Phase 1: Multimodal Evaluator Preference    ║
║  Text (12) + Visual (10) | GPT-4o Evaluator          ║
╚══════════════════════════════════════════════════════╝
""")
    
    print(f"Task: {len(TEXT_TASKS)} text + {len(VISUAL_TASKS)} visual = {len(ALL_TASKS)} total")
    print(f"Strategies: {len(STRATEGIES)} (8 text + 3 visual)")
    print(f"Evaluator: GPT-4o (cross-model)")
    print()
    
    result = run_condition("MM_EPC", gpt4o_eval, rounds_per_modality=8)
    
    print(f"""
═══ MM-EPC Phase 1 Results ═══
Rounds: {result['rounds']} | Time: {result['time']}s

PCI (overall):     {result['pci']}
PCI (text only):   {result['text_pci']}
PCI (visual only): {result['visual_pci']}
CPCI (cross-modal):{result['cpci']}
MPCI (multimodal): {result['mpci']}

Top strategy (overall): {result['top']} ({result['top_w']})
Top strategy (text):    {result['text_top']}
Top strategy (visual):  {result['visual_top']}

Strategy weights:
""")
    for k, v in sorted(result['weights'].items(), key=lambda x: -x[1]):
        tag = ""
        if k == result['top']: tag = " ← overall best"
        if k == result['text_top']: tag += " [text]"
        if k == result['visual_top']: tag += " [visual]"
        bar = "█" * int(v * 40)
        print(f"  {k:20s} {v:.3f} {bar}{tag}")
    
    print(f"""
🔬 Key findings:
  Text PCI = {result['text_pci']} | Visual PCI = {result['visual_pci']}
  Cross-modal CPCI = {result['cpci']} (higher = more divergence between modalities)
  MPCI = {result['mpci']}
""")
    
    if result['text_top'] != result['visual_top']:
        print(f"  ✅ CROSS-MODAL DIVERGENCE DETECTED!")
        print(f"     Text optimal: {result['text_top']} ≠ Visual optimal: {result['visual_top']}")
        print(f"     The evaluator prefers different strategies for different modalities.")
    
    # Save
    os.makedirs("/mnt/c/Users/Administrator/Desktop/aettl-research/experiments", exist_ok=True)
    filename = f"/mnt/c/Users/Administrator/Desktop/aettl-research/experiments/mm_epc_phase1.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 {filename}")
