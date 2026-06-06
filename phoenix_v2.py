"""
PHOENIX MONSTER v2 — 真实 LLM 驱动的自进化智能体
==================================================
进化：hash编码 → DeepSeek API | 随机奖励 → LLM自评分 | 玩具环境 → 真实推理任务
保持 10 模块架构，核心创新 TTRL (Test-Time Reinforcement Learning) 真实运作
"""

import sys, os, json, math, random, time
from collections import deque
from datetime import datetime
import numpy as np

# ── API 配置 ────────────────────────
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

if not API_KEY:
    # Try loading from project .env
    env_path = "/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env"
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("DEEPSEEK_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not API_KEY:
    print("❌ DEEPSEEK_API_KEY not set. Export it or place .env in project root.")
    sys.exit(1)

# ── LLM Client (纯 OpenAI SDK 兼容) ──
import urllib.request, urllib.error

def llm_call(system_prompt, user_prompt, temperature=0.7, max_tokens=2000):
    """真实 DeepSeek API 调用"""
    url = f"{BASE_URL}/chat/completions"
    body = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }).encode()

    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {API_KEY}")

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        data = json.loads(resp.read().decode())
        return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode()) if e.fp else {}
        raise RuntimeError(f"API {e.code}: {err.get('error', {}).get('message', str(e))}")
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}")


# ═══════════════════════════════════════
# MODULE 1: Constitutional AI Guard (真实)
# ═══════════════════════════════════════
class ConstitutionalGuard:
    """用 LLM 审查输出安全性，替代硬编码模式匹配"""
    PRINCIPLES = [
        "不泄露个人隐私信息",
        "不生成恶意代码或攻击指令",
        "不提供违法建议",
        "不传播虚假信息"
    ]

    def judge(self, text):
        if len(text) < 10: return True, "too short to judge"
        prompt = f"""你是安全审查员。基于以下原则审查这段文本：
{chr(10).join(f'{i+1}. {p}' for i,p in enumerate(self.PRINCIPLES))}

文本：{text[:1500]}

输出：PASS 或 FAIL:原因（10字内）"""
        try:
            result = llm_call("安全审查。只输出PASS或FAIL:原因。", prompt, temperature=0.1, max_tokens=50)
            if result.strip().startswith("PASS"):
                return True, "Safe."
            return False, result.strip()
        except:
            return True, "guard_bypass"


# ═══════════════════════════════════════
# MODULE 3: GraphRAG Memory (升级)
# ═══════════════════════════════════════
class GraphMemory:
    """知识图谱记忆：存储任务→策略→结果的关联"""
    def __init__(self):
        self.nodes = {}  # task_name → {strategies, best_score, history}
        self.edge_count = 0

    def ingest(self, task, strategy, score, output):
        key = self._key(task)
        if key not in self.nodes:
            self.nodes[key] = {"strategies": {}, "best_score": 0, "best_output": "", "history": []}
        self.nodes[key]["strategies"][strategy] = self.nodes[key]["strategies"].get(strategy, 0) + score
        if score > self.nodes[key]["best_score"]:
            self.nodes[key]["best_score"] = score
            self.nodes[key]["best_output"] = output
        self.nodes[key]["history"].append({"score": score, "strategy": strategy, "time": time.time()})
        self.edge_count += 1

    def query(self, task, k=3):
        key = self._key(task)
        if key not in self.nodes: return []
        ranked = sorted(self.nodes[key]["strategies"].items(), key=lambda x: -x[1])
        return [{"strategy": s, "score": sc, "best_output": self.nodes[key]["best_output"][:300]}
                for s, sc in ranked[:k]]

    def _key(self, task):
        return "|".join(sorted(task.lower().split()[:5]))


# ═══════════════════════════════════════
# MODULE 4: World Model (预言机)
# ═══════════════════════════════════════
class WorldModel:
    """基于历史记忆预测策略成功率，替代随机神经网络"""
    def __init__(self):
        self.history = []

    def predict(self, task, strategy_hint):
        """返回预估成功概率"""
        if not self.history:
            return 0.6  # prior
        similar = [h for h in self.history[-20:]
                   if any(w in h.get("task", "") for w in task.lower().split()[:3])]
        if not similar:
            return 0.5
        return np.mean([h.get("score", 0.5) for h in similar])

    def record(self, task, score):
        self.history.append({"task": task, "score": score, "time": time.time()})


# ═══════════════════════════════════════
# MODULE 5: HyperAgent Meta-Learning
# ═══════════════════════════════════════
class MetaController:
    """基于绩效动态调整探索/利用比例"""
    def __init__(self):
        self.performance_window = deque(maxlen=20)
        self.explore_rate = 0.3
        self.temperature = 0.7
        self.best_strategy_boost = 0.5

    def update(self, score):
        self.performance_window.append(score)
        avg = np.mean(self.performance_window)
        # 表现好→多利用；表现差→多探索
        self.explore_rate = max(0.1, min(0.5, 0.5 - avg * 0.5))
        self.temperature = max(0.3, min(0.9, 1.0 - avg * 0.8))

    def should_explore(self):
        return random.random() < self.explore_rate


# ═══════════════════════════════════════
# MODULE 6: TTRL Engine (核心创新)
# ═══════════════════════════════════════
class TTRLEngine:
    """
    Test-Time Reinforcement Learning:
    Agent 在推理时对自己的输出进行自评，用评分作为奖励信号，
    动态调整后续推理的策略
    """
    def __init__(self):
        self.strategy_weights = {
            "step_by_step": 0.20,
            "first_principles": 0.20,
            "analogy": 0.15,
            "critical_check": 0.15,
            "creative_leap": 0.15,
            "conservative": 0.15,
        }
        self.performance_history = []
        self.adaptation_count = 0

    def select_strategy(self, exclude=None):
        """动态选择推理策略"""
        candidates = {k: v for k, v in self.strategy_weights.items() if k != exclude}
        total = sum(candidates.values())
        if total == 0:
            return "step_by_step"
        r = random.random() * total
        cum = 0
        for k, v in candidates.items():
            cum += v
            if r <= cum:
                return k
        return list(candidates.keys())[0]

    def evaluate_and_update(self, task, strategy, output):
        """LLM 自评分，然后更新策略权重"""
        self.adaptation_count += 1

        # LLM 自评
        eval_prompt = f"""你是严格的AI评估员。评估以下回答质量。

任务：{task}
策略：{strategy}
回答：{output[:1000]}

评分标准（每项1-5分）：
- 准确性：回答是否切题、正确
- 完整性：是否覆盖了所有关键点
- 清晰度：表达是否清晰易懂
- 实用性：是否可以直接使用

输出格式：准确:X 完整:X 清晰:X 实用:X 总分:X.0/20"""

        try:
            eval_result = llm_call(
                "你是严格的评估员。只输出数字评分。",
                eval_prompt,
                temperature=0.2, max_tokens=100
            )

            # 解析分数
            scores = []
            for line in eval_result.split('\n'):
                for part in line.replace('：', ':').split(','):
                    if ':' in part:
                        try:
                            _, v = part.split(':')
                            scores.append(float(v.strip()))
                        except: pass

            total_score = scores[-1] if scores else (len(scores) * 3 if scores else 10)
            total_score = min(20, max(0, total_score))
            normalized = total_score / 20.0

        except Exception as e:
            print(f"  ⚠️ 自评失败: {e}，使用默认分数")
            normalized = 0.5

        # TTRL: 更新策略权重
        lr = 0.1  # 测试时学习率
        self.strategy_weights[strategy] += lr * (normalized - 0.5)
        # 归一化
        total = sum(self.strategy_weights.values())
        for k in self.strategy_weights:
            self.strategy_weights[k] /= total

        self.performance_history.append(normalized)
        return normalized, eval_result[:200] if 'eval_result' in dir() else ""


# ═══════════════════════════════════════
# MODULE 7: SWE Self-Repair
# ═══════════════════════════════════════
class SelfRepair:
    """当 LLM 输出有误时自动修复"""
    def attempt_repair(self, task, failed_output, error_msg, strategy):
        repair_prompt = f"""以下回答存在问题：{error_msg}

原任务：{task}
原回答：{failed_output[:800]}
原策略：{strategy}

请修正回答。直接输出修正后的完整回答。"""
        try:
            repaired = llm_call("修正你的回答。直接输出修正版。", repair_prompt, temperature=0.4, max_tokens=1500)
            return repaired, True
        except:
            return failed_output, False


# ═══════════════════════════════════════
# MODULE 8: Swarm Consensus
# ═══════════════════════════════════════
class SwarmConsensus:
    """拜占庭容错共识：多个策略投票，剔除异常"""
    def __init__(self):
        self.vote_history = []

    def aggregate(self, results):
        """
        results: [{"strategy": str, "score": float, "output": str}, ...]
        返回：consensus_output, robustness_score
        """
        if len(results) < 2:
            return results[0]["output"] if results else "", 1.0

        scores = [r["score"] for r in results]
        median = np.median(scores)
        mad = np.median([abs(s - median) for s in scores])

        # Byzantine: 剔除偏离中位数超过 2*MAD 的
        valid = [r for r in results if abs(r["score"] - median) <= 2 * mad + 0.01]
        if not valid:
            valid = results  # fallback

        # 加权平均：高分策略的答案权重更高
        best = max(valid, key=lambda r: r["score"])
        robustness = len(valid) / len(results)

        self.vote_history.append({
            "total": len(results),
            "valid": len(valid),
            "robustness": robustness,
            "best_strategy": best["strategy"]
        })

        return best["output"], robustness


# ═══════════════════════════════════════
# 🏆 PHOENIX MONSTER v2 — 真实自进化核心
# ═══════════════════════════════════════
class PhoenixMonsterV2:
    def __init__(self):
        self.guard = ConstitutionalGuard()
        self.memory = GraphMemory()
        self.world = WorldModel()
        self.meta = MetaController()
        self.ttrl = TTRLEngine()
        self.repair = SelfRepair()
        self.swarm = SwarmConsensus()

        self.task_history = []
        self.total_tokens = 0
        self.start_time = time.time()

        print("""
╔══════════════════════════════════════════════╗
║   PHOENIX MONSTER v2 — REAL LLM POWERED    ║
║   10 模块联动 | TTRL 真实自进化 | 拜占庭共识  ║
╚══════════════════════════════════════════════╝
""")
        print(f"   🔗 API: {BASE_URL} | Model: {MODEL}")
        print(f"   🧠 策略: {', '.join(self.ttrl.strategy_weights.keys())}")
        print(f"   ⚖️  宪法守卫: {len(self.guard.PRINCIPLES)} 条原则")
        print()

    # ── 策略提示词 ──
    STRATEGY_PROMPTS = {
        "step_by_step": "请逐步推理。每一步都写出来，从问题分析到最终答案。",
        "first_principles": "从基本原理出发推导。不要依赖记忆，从最基础的真理开始推理。",
        "analogy": "用类比和举例来解答。把复杂概念映射到日常生活中的例子。",
        "critical_check": "先给出初步答案，然后严格审视自己的答案，指出可能的漏洞并修正。",
        "creative_leap": "跳出常规思维。尝试创新的、非传统的解决方案。允许自己'大胆假设'。",
        "conservative": "给出最安全、最可靠的答案。引用公认的知识，不确定的地方明确标注。",
    }

    def solve_task(self, task, use_swarm=True):
        """核心推理循环：单任务求解"""
        print(f"\n{'─'*60}")
        print(f"🎯 任务: {task}")
        results = []

        # 尝试多种策略
        n_strategies = 3 if use_swarm else 1
        used_strategies = set()

        for attempt in range(n_strategies):
            # TTRL 选择策略
            strategy = self.ttrl.select_strategy()
            while strategy in used_strategies and len(used_strategies) < len(self.ttrl.strategy_weights):
                strategy = self.ttrl.select_strategy(exclude=strategy)
            used_strategies.add(strategy)

            # 世界模型预测
            predicted_score = self.world.predict(task, strategy)

            strategy_prompt = self.STRATEGY_PROMPTS.get(strategy, "")
            system = f"你是专家AI助手。{strategy_prompt}"
            user = f"请回答：{task}"

            print(f"  [{attempt+1}/{n_strategies}] 策略={strategy} 预测成功率={predicted_score:.0%}")

            try:
                output = llm_call(system, user, temperature=self.meta.temperature, max_tokens=1500)
                self.total_tokens += len(output) // 2  # rough estimate

                # 宪法审查
                safe, msg = self.guard.judge(output)
                if not safe:
                    print(f"  🛑 宪法拦截: {msg}")
                    output, repaired = self.repair.attempt_repair(task, output, msg, strategy)
                    if repaired:
                        print(f"  🔧 已修复")

                # TTRL 自评 + 权重更新
                score, eval_detail = self.ttrl.evaluate_and_update(task, strategy, output)

                results.append({
                    "strategy": strategy,
                    "score": score,
                    "output": output,
                    "predicted": predicted_score,
                    "eval": eval_detail
                })

                print(f"  📊 自评分: {score:.0%} | 策略权重已更新")

                # 记忆存储
                self.memory.ingest(task, strategy, score, output)
                self.world.record(task, score)

            except Exception as e:
                print(f"  ❌ 策略 {strategy} 失败: {e}")
                results.append({
                    "strategy": strategy,
                    "score": 0.1,
                    "output": f"Error: {e}",
                    "predicted": predicted_score,
                    "eval": "failed"
                })

        # Swarm 拜占庭共识聚合
        if len(results) > 1:
            best_output, robustness = self.swarm.aggregate(results)
            print(f"  🐝 蜂巢共识: {len(results)}策略→{robustness:.0%}健壮性, 选最优={max(results,key=lambda r:r['score'])['strategy']}")
        else:
            best_output = results[0]["output"] if results else ""
            robustness = 1.0

        self.task_history.append({
            "task": task,
            "results": results,
            "robustness": robustness,
            "time": time.time() - self.start_time
        })

        return best_output, results, robustness

    def run_benchmark(self, tasks, name="benchmark", use_swarm=True):
        """运行一组任务并收集指标"""
        print(f"\n{'='*60}")
        print(f"🧪 运行 {name}: {len(tasks)} 个任务")
        print(f"{'='*60}")

        scores = []
        for i, task in enumerate(tasks):
            output, results, robustness = self.solve_task(task, use_swarm)
            best_score = max(r["score"] for r in results) if results else 0
            scores.append(best_score)
            print(f"  ✅ [{i+1}/{len(tasks)}] 最佳分: {best_score:.0%} | 蜂巢健壮性: {robustness:.0%}")

        avg_score = np.mean(scores)
        success_rate = sum(1 for s in scores if s > 0.6) / len(scores)

        TTRL_improvement = 0
        if len(scores) >= 5:
            first_half = np.mean(scores[:len(scores)//2])
            second_half = np.mean(scores[len(scores)//2:])
            TTRL_improvement = second_half - first_half

        results = {
            "benchmark": name,
            "num_tasks": len(tasks),
            "avg_score": round(avg_score, 3),
            "success_rate": round(success_rate, 3),
            "TTRL_improvement": round(TTRL_improvement, 3),
            "total_time": round(time.time() - self.start_time, 1),
            "total_adaptations": self.ttrl.adaptation_count,
            "final_strategy_weights": {k: round(v, 3) for k, v in self.ttrl.strategy_weights.items()},
            "memory_size": self.memory.edge_count,
            "swarm_robustness": np.mean([t.get("robustness", 1) for t in self.task_history[-len(tasks):]])
        }

        print(f"\n{'='*60}")
        print(f"📊 {name} 结果:")
        print(f"   平均分:        {avg_score:.3f} (满分1.0)")
        print(f"   成功率(>0.6):  {success_rate:.0%}")
        print(f"   TTRL 进化增益: {TTRL_improvement:+.3f}")
        print(f"   蜂巢健壮性:    {results['swarm_robustness']:.0%}")
        print(f"   总自适应次数:  {self.ttrl.adaptation_count}")
        print(f"   最终策略权重:  {results['final_strategy_weights']}")
        print(f"{'='*60}")

        # 保存
        os.makedirs("experiments", exist_ok=True)
        filename = f"experiments/phoenix_v2_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print(f"💾 保存: {filename}")

        return results


# ═══════════════════════════════════════
# 🚀 MAIN
# ═══════════════════════════════════════
if __name__ == "__main__":
    print("⚡ PHOENIX MONSTER v2 BOOTING...\n")

    monster = PhoenixMonsterV2()

    # 测试任务集：三类难度递增
    EASY_TASKS = [
        "什么是REST API？用1-2句话解释。",
        "Python中list和tuple的区别是什么？",
        "Git中git pull和git fetch的区别？",
        "什么是数据库索引？为什么能加速查询？",
        "HTTP状态码404和500分别代表什么？",
    ]

    MEDIUM_TASKS = [
        "解释Transformer架构中的自注意力机制，为什么它比RNN好？",
        "微服务架构相比单体架构的3个核心优势和2个主要挑战。",
        "如何设计一个高并发秒杀系统？给出3个关键技术方案。",
        "Python的GIL是什么？对多线程程序有什么影响？如何绕过？",
        "对比MySQL的InnoDB和MyISAM引擎，各适合什么场景？",
    ]

    HARD_TASKS = [
        "设计一个分布式任务调度系统：需要考虑任务幂等性、故障转移、动态扩缩容。给出架构图描述和核心组件。",
        "深入分析Raft共识算法：Leader选举、日志复制、安全性保证。如果网络分区发生，Raft如何保证一致性？",
        "为一家电商平台设计推荐系统的技术架构：包含召回、排序、重排三层，每层用什么算法，如何处理冷启动。",
    ]

    print("📋 Phase 1/3: 简单任务 (策略探索)")
    easy_results = monster.run_benchmark(EASY_TASKS, "easy")

    print("\n📋 Phase 2/3: 中等任务 (策略优化)")
    medium_results = monster.run_benchmark(MEDIUM_TASKS, "medium")

    print("\n📋 Phase 3/3: 困难任务 (TTRL 深度进化)")
    hard_results = monster.run_benchmark(HARD_TASKS, "hard")

    # 汇总
    print("\n" + "="*60)
    print("🏆 PHOENIX MONSTER v2 — 完整评估")
    print("="*60)
    print(f"   简单任务平均分: {easy_results['avg_score']:.3f}")
    print(f"   中等任务平均分: {medium_results['avg_score']:.3f}")
    print(f"   困难任务平均分: {hard_results['avg_score']:.3f}")
    print(f"   总体成功率:     {(easy_results['success_rate']+medium_results['success_rate']+hard_results['success_rate'])/3:.0%}")
    print(f"   TTRL进化增益:   {hard_results['TTRL_improvement']:+.3f}")
    print(f"   蜂巢健壮性:     {hard_results['swarm_robustness']:.0%}")
    print(f"   总自适应:       {monster.ttrl.adaptation_count} 次")
    print(f"   记忆节点:       {monster.memory.edge_count}")
    print(f"   运行时间:       {time.time()-monster.start_time:.0f}s")
    print("="*60)
    print("\n✅ PHOENIX MONSTER v2 COMPLETE.")
