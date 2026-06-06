"""
PHOENIX MONSTER v4 — 进化修复版
═══════════════════════════════════════
修复1: 交叉模型评估 — Claude评DeepSeek (打破自评循环)
修复2: 排序比较 — A/B对比替代数字评分 (增加区分度)
修复3: 多类型任务 — 代码+推理+规划+对话 (提升多样性)
修复4: 基准验证 — 可验证答案的正确率统计
修复5: 对照组 — 固定策略 vs TTRL 并行对比
"""

import json, os, time, urllib.request, random
from collections import deque
from datetime import datetime

# ── Keys ──
env_path = "/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env"
DS_KEY = ""
for line in open(env_path):
    if line.startswith("DEEPSEEK_API_KEY="):
        DS_KEY = line.split("=",1)[1].strip().strip('"').strip("'")

api2d_key = "fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7"  # Claude via api2d

# ── LLM Clients ──
def llm_deepseek(sp, up, temp=0.7, mt=800):
    b = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp},{"role":"user","content":up}],"max_tokens":mt,"temperature":temp}).encode()
    r = urllib.request.Request("https://api.deepseek.com/chat/completions", data=b, method="POST")
    r.add_header("Content-Type","application/json")
    r.add_header("Authorization",f"Bearer {DS_KEY}")
    return json.loads(urllib.request.urlopen(r,timeout=60).read().decode())["choices"][0]["message"]["content"]

def llm_claude(sp, up, temp=0.3, mt=300):
    """Claude via api2d as external evaluator"""
    b = json.dumps({"model":"claude-3-5-haiku-20241022","max_tokens":mt,"temperature":temp,"system":sp,"messages":[{"role":"user","content":up}]}).encode()
    r = urllib.request.Request("https://oa.api2d.net/v1/messages", data=b, method="POST")
    r.add_header("Content-Type","application/json")
    r.add_header("Authorization",f"Bearer {api2d_key}")
    r.add_header("x-api2d-no-cache","true")
    return json.loads(urllib.request.urlopen(r,timeout=60).read().decode())["content"][0]["text"]

# ── Cross-Model Evaluator ──
def cross_model_compare(task, answer_a, answer_b, strategy_a, strategy_b):
    """Claude does A/B comparison (fixes circular self-eval + adds discrimination)"""
    prompt = f"""你是公正的AI评估员。比较两个回答，选出更好的。

任务：{task}

回答A (策略:{strategy_a})：
{answer_a[:600]}

回答B (策略:{strategy_b})：
{answer_b[:600]}

比较标准：
- 是否准确切题
- 逻辑是否清晰
- 是否有具体依据而非泛泛而谈
- 是否可以直接用于解决问题

只输出：A 或 B （哪个更好）"""
    
    try:
        result = llm_claude("你是公正的评估员。", prompt, temp=0.1, mt=50).strip().upper()
        if "A" in result and "B" not in result:
            return "A"
        elif "B" in result:
            return "B"
        return random.choice(["A","B"])
    except:
        # If Claude unavailable, fallback to DeepSeek cross-eval
        try:
            result = llm_deepseek("公正评估员。", prompt, temp=0.1, mt=50).strip().upper()
            return "A" if "A" in result else "B"
        except:
            return random.choice(["A","B"])


# ═══════════════════════════════════
# MULTI-TYPE TASK BANK (fixes task diversity)
# ═══════════════════════════════════
BENCHMARK_TASKS = [
    # ── 可验证答案 (正确/错误) ──
    {"type":"verify","q":"1+2*3等于多少？","answer":"7","hint":"先乘后加"},
    {"type":"verify","q":"Python中 5//2 的结果是多少？","answer":"2","hint":"整除运算"},
    {"type":"verify","q":"TCP端口号范围是多少？","answer":"0到65535","hint":"16位无符号整数"},
    {"type":"verify","q":"Git中撤销最近一次commit但不丢失修改的命令？","answer":"git reset --soft HEAD~1","hint":"soft reset"},
    {"type":"verify","q":"SQL中LIMIT 10 OFFSET 20会跳过多少行？","answer":"20","hint":"OFFSET就是跳过行数"},
    
    # ── 代码生成 ──
    {"type":"code","q":"用Python写一个函数，判断字符串是否回文。","hint":"双指针或切片"},
    {"type":"code","q":"用Python写一个二分查找函数，返回目标索引或-1。","hint":"while left<=right"},
    {"type":"code","q":"写一个Python装饰器，记录函数执行时间。","hint":"time.time()前后差值"},
    
    # ── 推理任务 ──
    {"type":"reasoning","q":"如果所有的A都是B，所有的B都是C，那么所有的A都是C。这个推理对吗？为什么？","hint":"三段论"},
    {"type":"reasoning","q":"一个房间有3盏灯，门外有3个开关。你只能进房间一次，如何确定哪个开关控制哪盏灯？","hint":"灯泡会发热"},
    {"type":"reasoning","q":"你有8枚硬币，其中1枚是假币（更轻）。用天平最少称几次能找到假币？","hint":"二分法"},
    
    # ── 规划/设计 ──
    {"type":"design","q":"设计一个URL短链接系统。需要哪些核心组件？","hint":"hash+数据库+重定向"},
    {"type":"design","q":"设计一个分布式ID生成器，要求全局唯一、趋势递增。","hint":"Snowflake算法"},
    
    # ── 技术解释 ──
    {"type":"explain","q":"为什么数据库索引用B+树而不是二叉搜索树？","hint":"磁盘IO"},
    {"type":"explain","q":"解释HTTPS握手过程中证书验证的步骤。","hint":"CA链"},
]

STRATEGIES = {
    "step_by_step": "逐步推理，每步写清逻辑",
    "critical_check": "先给出答案，再审视修正",
    "first_principles": "从基本原理推导",
    "creative_leap": "创新方案，不限于常规",
    "analogy_meta": "用类比和举例解释",
    "evidence_cite": "引用具体知识点依据",
    "synthesis": "综合多视角平衡回答",
    "counterfactual": "考虑反面情况和边界",
}

# ═══════════════════════════════════
# EVOLUTION ENGINE v4
# ═══════════════════════════════════
class EvolutionV4:
    def __init__(self):
        self.weights = {k: 1/len(STRATEGIES) for k in STRATEGIES}
        self.history = []
        self.control_history = []  # Fixed-strategy control group
        self.correct_count = 0
        self.control_correct = 0
        self.total_verify = 0
        self.cross_model_comparisons = 0
        self.comparison_wins = {k:0 for k in STRATEGIES}
    
    def select_strategy(self):
        r = random.random() * sum(self.weights.values())
        cum = 0
        for k, v in self.weights.items():
            cum += v
            if r <= cum: return k
        return list(self.weights.keys())[-1]
    
    def verify_answer(self, task, output):
        """Check if answer contains expected answer (for benchmark tasks)"""
        if task["type"] != "verify": return None
        expected = task["answer"].lower()
        actual = output.lower()
        # Simple substring match
        return expected in actual
    
    def run_round(self, task, round_num):
        result = {"round": round_num + 1, "type": task["type"]}
        
        # ── TTRL Group ──
        strategy = self.select_strategy()
        sp = f"你是专家AI。策略：{STRATEGIES[strategy]}"
        up = task["q"]
        if "hint" in task:
            up += f"\n\n提示：{task['hint']}"
        
        try:
            # TTRL solve
            output = llm_deepseek(sp, up, temp=0.7, mt=600)
            
            # Control: use fixed "step_by_step" strategy
            control_output = llm_deepseek(
                f"你是专家AI。策略：逐步推理。",
                up, temp=0.7, mt=600
            )
            
            # ── Cross-model A/B comparison (vs control) ──
            winner = cross_model_compare(
                task["q"],
                output, control_output,
                strategy, "step_by_step(对照)"
            )
            self.cross_model_comparisons += 1
            
            if winner == "A":  # TTRL strategy won
                self.comparison_wins[strategy] += 1
                update = 0.08  # strong positive
            else:  # Control (step_by_step) won
                update = -0.03  # mild negative
            
            # TTRL weight update
            self.weights[strategy] += update
            total = sum(self.weights.values())
            self.weights = {k: max(0.01, v/total) for k, v in self.weights.items()}
            # Renormalize
            total = sum(self.weights.values())
            self.weights = {k: v/total for k, v in self.weights.items()}
            
            # ── Benchmark verification ──
            correct = self.verify_answer(task, output)
            control_correct = self.verify_answer(task, control_output)
            if correct is not None:
                self.total_verify += 1
                if correct: self.correct_count += 1
                if control_correct: self.control_correct += 1
            
            result.update({
                "strategy": strategy,
                "winner": winner,
                "correct": correct,
                "control_correct": control_correct,
                "top_strategy": max(self.weights, key=self.weights.get),
                "top_weight": round(self.weights[max(self.weights, key=self.weights.get)], 3),
            })
            
            return result
            
        except Exception as e:
            result["error"] = str(e)[:80]
            return result
    
    def run_benchmark(self, tasks, rounds=100):
        print(f"🔥 PHOENIX v4 — {rounds}轮进化")
        print(f"  修复: 交叉模型评估 | A/B排序 | 多类型任务 | 基准验证 | 对照组")
        print(f"  任务: {len(tasks)}个 ({','.join(set(t['type'] for t in tasks))})")
        print()
        
        t0 = time.time()
        for rnd in range(rounds):
            task = tasks[rnd % len(tasks)]
            result = self.run_round(task, rnd)
            self.history.append(result)
            
            if (rnd + 1) % 10 == 0:
                elapsed = time.time() - t0
                wins = sum(1 for h in self.history[-10:] if h.get("winner") == "A")
                correct_rate = self.correct_count / max(1, self.total_verify)
                print(f"  [r{rnd+1:3d}] TTRL胜率:{wins}/10={wins*10}% | "
                      f"正确率:{correct_rate:.0%} | "
                      f"最优:{max(self.weights,key=self.weights.get)} | "
                      f"耗时:{elapsed:.0f}s")
            
            time.sleep(1.2)
        
        elapsed = time.time() - t0
        return {
            "rounds": rounds,
            "total_time": elapsed,
            "cross_model_comparisons": self.cross_model_comparisons,
            "ttrl_win_rate": sum(1 for h in self.history if h.get("winner")=="A") / max(1, len([h for h in self.history if "winner" in h])),
            "ttrl_correct_rate": self.correct_count / max(1, self.total_verify),
            "control_correct_rate": self.control_correct / max(1, self.total_verify),
            "final_weights": {k: round(v, 3) for k, v in self.weights.items()},
            "strategy_wins": self.comparison_wins,
        }


# ═══════════════════════════════════
# RUN
# ═══════════════════════════════════
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════╗
║  PHOENIX MONSTER v4 — 进化修复版             ║
║  交叉模型评估 | A/B排序 | 多类型 | 基准 | 对照 ║
╚══════════════════════════════════════════════╝
""")
    
    engine = EvolutionV4()
    results = engine.run_benchmark(BENCHMARK_TASKS, rounds=60)
    
    print(f"""
{'='*55}
🏆 PHOENIX v4 — 最终结果
{'='*55}
交叉模型评估次数:  {results['cross_model_comparisons']}

TTRL vs 对照(固定step_by_step):
  TTRL 胜率:       {results['ttrl_win_rate']:.1%}
  TTRL 正确率:     {results['ttrl_correct_rate']:.1%}
  对照正确率:      {results['control_correct_rate']:.1%}
  正确率差异:      {results['ttrl_correct_rate']-results['control_correct_rate']:+.1%}

策略A/B对战获胜次数:
""")
    for k, v in sorted(results['strategy_wins'].items(), key=lambda x: -x[1]):
        bar = "█" * v
        print(f"  {k:20s} {v:2d}胜 {bar}")
    
    print(f"""
最终策略权重:
""")
    for k, v in sorted(results['final_weights'].items(), key=lambda x: -x[1]):
        bar = "█" * int(v * 50)
        print(f"  {k:20s} {v:.3f} {bar}")
    
    print(f"""
  🏆 最优: {max(results['final_weights'],key=results['final_weights'].get)}
  💀 淘汰: {min(results['final_weights'],key=results['final_weights'].get)}
{'='*55}
""")
    
    # Save
    os.makedirs("/mnt/c/Users/Administrator/Desktop/aettl-research/experiments", exist_ok=True)
    with open(f"/mnt/c/Users/Administrator/Desktop/aettl-research/experiments/v4_final.json","w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print("💾 experiments/v4_final.json")
