"""
PHOENIX MONSTER v3 — 百轮自进化 + 300篇论文反思
=================================================
论文采集 → 洞察提取 → 策略进化 → 任务求解 → 自我反思 → (循环100轮)
"""

import urllib.request, urllib.parse, json, os, sys, time, re
from collections import deque, Counter
from datetime import datetime
import xml.etree.ElementTree as ET

API_KEY = ""
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"

# Load key
env_path = "/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env"
if os.path.exists(env_path):
    for line in open(env_path):
        if line.startswith("DEEPSEEK_API_KEY="):
            API_KEY = line.split("=",1)[1].strip().strip('"').strip("'")
if not API_KEY:
    print("❌ No API key"); sys.exit(1)

def llm(sp, up, temp=0.7, mt=1500):
    url = f"{BASE_URL}/chat/completions"
    body = json.dumps({"model":MODEL,"messages":[{"role":"system","content":sp},{"role":"user","content":up}],"max_tokens":mt,"temperature":temp}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type","application/json")
    req.add_header("Authorization",f"Bearer {API_KEY}")
    resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read().decode())["choices"][0]["message"]["content"]

def llm_quick(msg, mt=300):
    return llm("简洁回答。", msg, temp=0.3, mt=mt)

# ═══════════════════════════════════════
# PHASE 1: 论文采集引擎
# ═══════════════════════════════════════
class PaperCollector:
    """ArXiv API: 多领域采集300+篇论文摘要"""
    
    CATEGORIES = {
        "LLM": ["cs.CL", "cs.AI"],
        "RL": ["cs.LG", "cs.AI"],
        "CV": ["cs.CV"],
        "Agent": ["cs.AI", "cs.MA"],
        "Reasoning": ["cs.CL", "cs.AI"],
        "Safety": ["cs.CR", "cs.AI"],
    }
    
    SEARCH_QUERIES = [
        "large language model agent reasoning",
        "test time training reinforcement learning",
        "multi agent system consensus coordination",
        "chain of thought reasoning prompt engineering",
        "language model self improvement self play",
        "retrieval augmented generation knowledge",
        "code generation agent software engineering",
        "AI safety alignment constitutional",
        "mixture of experts sparse routing",
        "agent tool use function calling",
        "reasoning language model",
        "agent planning decision making",
        "reinforcement learning from feedback",
        "knowledge graph reasoning",
        "embodied agent robotics planning",
    ]
    
    def __init__(self):
        self.papers = []
        self.insights = []
        
    def fetch(self, max_per_query=20):
        print(f"\n{'='*60}")
        print(f"📚 PHASE 1: 论文采集 — ArXiv API")
        print(f"{'='*60}")
        
        for query in self.SEARCH_QUERIES:
            try:
                papers = self._search_arxiv(query, max_per_query)
                self.papers.extend(papers)
                print(f"  📄 '{query[:50]}...' → {len(papers)} 篇")
                time.sleep(1)  # Rate limit
            except Exception as e:
                print(f"  ⚠️ '{query[:30]}...' → {e}")
        
        # 去重
        seen = set()
        unique = []
        for p in self.papers:
            if p["id"] not in seen:
                seen.add(p["id"])
                unique.append(p)
        self.papers = unique
        
        print(f"\n  📊 采集完成: {len(self.papers)} 篇唯一论文")
        return self.papers
    
    def _search_arxiv(self, query, max_results):
        base = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        url = f"{base}?{urllib.parse.urlencode(params)}"
        
        req = urllib.request.Request(url, headers={"User-Agent": "PhoenixMonster/3.0"})
        resp = urllib.request.urlopen(req, timeout=30)
        data = resp.read().decode()
        
        root = ET.fromstring(data)
        papers = []
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            id_el = entry.find("atom:id", ns)
            
            title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""
            summary = summary_el.text.strip()[:800] if summary_el is not None else ""
            paper_id = id_el.text.strip() if id_el is not None else ""
            
            if title and summary:
                papers.append({"id": paper_id, "title": title, "abstract": summary})
        
        return papers


# ═══════════════════════════════════════
# PHASE 2: 论文反思引擎
# ═══════════════════════════════════════
class PaperReflector:
    """用 LLM 批量提取论文洞察"""
    
    def __init__(self):
        self.insight_pool = []  # List of {category, insight, confidence}
        self.categories = Counter()
        
    def reflect_batch(self, papers, batch_size=15):
        print(f"\n{'='*60}")
        print(f"🧠 PHASE 2: 论文反思 — {len(papers)} 篇论文")
        print(f"{'='*60}")
        
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i+batch_size]
            insights = self._extract_insights(batch)
            self.insight_pool.extend(insights)
            
            for ins in insights:
                self.categories[ins["category"]] += 1
            
            progress = min(i+batch_size, len(papers))
            print(f"  📖 [{progress}/{len(papers)}] 提取 {len(insights)} 条洞察 | 累计 {len(self.insight_pool)} 条")
            time.sleep(0.5)
        
        print(f"\n  📊 洞察分布: {dict(self.categories.most_common(10))}")
        return self.insight_pool
    
    def _extract_insights(self, batch):
        papers_text = "\n\n".join([
            f"论文{i+1}: {p['title'][:150]}\n摘要: {p['abstract'][:500]}"
            for i, p in enumerate(batch)
        ])
        
        prompt = f"""你是AI研究员。从以下论文中提取3-5条最有价值的洞察。

每行格式: 类别|洞察内容
类别只能选: REASONING(推理方法), ARCHITECTURE(架构设计), TRAINING(训练技巧), SAFETY(安全对齐), AGENT(智能体), PROMPT(提示工程)

论文：
{papers_text[:8000]}

提取最有价值的3-5条洞察，每行一条。"""
        
        try:
            result = llm(prompt, "提取洞察。", temp=0.3, mt=600)
            insights = []
            for line in result.split('\n'):
                if '|' in line:
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        cat = parts[0].strip()
                        text = parts[1].strip()
                        if cat in ["REASONING","ARCHITECTURE","TRAINING","SAFETY","AGENT","PROMPT"]:
                            insights.append({"category": cat, "insight": text, "confidence": 0.7})
            return insights[:5]
        except:
            return []


# ═══════════════════════════════════════
# PHASE 3: 百轮进化核心
# ═══════════════════════════════════════
class EvolutionEngine:
    """基于论文洞察 + 任务反馈持续进化"""
    
    STRATEGIES = {
        "step_by_step": "逐步推理，每步写明逻辑",
        "critical_check": "先答后审，指出漏洞并修正",
        "first_principles": "从基本原理推导，不靠记忆",
        "creative_leap": "跳出常规，寻找创新方案",
        "analogy_meta": "用类比和例子解释",
        "evidence_cite": "引用具体知识点和论文依据",
        "counterfactual": "考虑反事实：如果不是这样会怎样",
        "synthesis": "综合多种视角，给出平衡答案",
    }
    
    def __init__(self):
        self.weights = {k: 1/len(self.STRATEGIES) for k in self.STRATEGIES}
        self.evolution_history = []
        self.insight_index = {}
        self.generation = 0
        self.total_score = 0
        self.total_calls = 0
    
    def incorporate_insights(self, insights):
        """论文洞察映射到策略权重调整"""
        for ins in insights:
            cat = ins["category"]
            text = ins["insight"]
            
            # 类别→策略映射
            if cat == "REASONING":
                if "step" in text.lower() or "chain" in text.lower():
                    self.weights["step_by_step"] += 0.02
                if "verify" in text.lower() or "check" in text.lower():
                    self.weights["critical_check"] += 0.02
            elif cat == "ARCHITECTURE":
                if "mixture" in text.lower() or "expert" in text.lower():
                    self.weights["synthesis"] += 0.02
            elif cat == "PROMPT":
                if "example" in text.lower() or "few" in text.lower():
                    self.weights["analogy_meta"] += 0.01
                if "instruction" in text.lower():
                    self.weights["step_by_step"] += 0.01
            elif cat == "AGENT":
                if "multi" in text.lower() or "cooperat" in text.lower():
                    self.weights["synthesis"] += 0.01
                    self.weights["critical_check"] += 0.01
            elif cat == "SAFETY":
                self.weights["critical_check"] += 0.015
                self.weights["evidence_cite"] += 0.01
            elif cat == "TRAINING":
                if "feedback" in text.lower() or "reward" in text.lower():
                    self.weights["critical_check"] += 0.02
            
            # Normalize
            total = sum(self.weights.values())
            self.weights = {k: v/total for k, v in self.weights.items()}
        
        self.generation += 1
    
    def select_strategy(self):
        """加权随机选择策略"""
        r = sum(self.weights.values()) * __import__('random').random()
        cum = 0
        for k, v in self.weights.items():
            cum += v
            if r <= cum: return k
        return list(self.weights.keys())[-1]
    
    def run_evolution_round(self, task_pool, round_num):
        """一轮进化：选任务→选策略→求解→自评→更新权重"""
        task = task_pool[round_num % len(task_pool)]
        strategy = self.select_strategy()
        strategy_desc = self.STRATEGIES[strategy]
        
        system = f"你是专家AI助手。回答策略：{strategy_desc}"
        user = f"请回答：{task}"
        
        try:
            output = llm(system, user, temp=0.7, mt=800)
            self.total_calls += 1
            
            # Self-eval
            eval_msg = f"""评估回答质量(各1-5分)。任务：{task}\n回答：{output[:800]}\n\n输出格式：准确:X 完整:X 清晰:X 深度:X 总分:X/20"""
            eval_result = llm_quick(eval_msg, mt=80)
            self.total_calls += 1
            
            # Parse score
            nums = [float(s) for s in eval_result.replace(':',' ').replace('/',' ').split() if s.replace('.','').isdigit()]
            score = nums[-1]/20 if nums else 0.5
            score = min(1.0, max(0.1, score))
            
            # TTRL update
            lr = 0.08
            self.weights[strategy] += lr * (score - 0.5)
            total = sum(self.weights.values())
            self.weights = {k: v/total for k, v in self.weights.items()}
            
            self.total_score += score
            avg = self.total_score / max(1, round_num + 1)
            
            record = {
                "round": round_num + 1,
                "task": task[:60],
                "strategy": strategy,
                "score": round(score, 3),
                "avg_score": round(avg, 3),
                "top_strategy": max(self.weights, key=self.weights.get),
                "weights_snapshot": {k: round(v,3) for k,v in sorted(self.weights.items(), key=lambda x:-x[1])[:4]},
            }
            self.evolution_history.append(record)
            
            return record
            
        except Exception as e:
            self.total_calls += 1
            return {"round": round_num+1, "task": task[:60], "strategy": strategy, "score": 0.1, "error": str(e)}


# ═══════════════════════════════════════
# PHASE 4: 主流程
# ═══════════════════════════════════════
TASK_BANK = [
    # 技术深度
    "Transformer的自注意力机制相比RNN的核心优势是什么？从计算复杂度和长程依赖两个角度分析。",
    "解释扩散模型的工作原理，为什么它比GAN生成质量更高？",
    "MoE(Mixture of Experts)架构如何实现稀疏激活？分析其相比Dense模型的优势和挑战。",
    "大模型幻觉(hallucination)的根因是什么？目前有哪些有效的缓解方案？",
    "对比RLHF和DPO两种对齐方法，各自的优缺点和适用场景。",
    "RAG系统的检索质量如何影响生成效果？讨论chunk策略、embedding选择和重排序。",
    "解释LoRA和QLoRA的原理，为什么它们能高效微调大模型？",
    "Chain-of-Thought提示为什么能提升推理能力？从认知科学角度分析。",
    "Agent如何实现可靠的工具调用？讨论function calling、错误处理和工具选择策略。",
    "多模态大模型的训练范式：对比学习 vs 生成式，各自的优劣。",
    # 工程实践
    "设计一个高可用AI推理服务，考虑负载均衡、模型热切换、请求优先级调度。",
    "如何评估一个LLM Agent系统的质量？设计一套完整的评测框架。",
    "大规模RAG系统的延迟优化：从检索到生成的端到端方案。",
    "AI Agent的安全边界设计：权限控制、输入消毒、输出过滤。",
    "构建可观测的AI系统：需要监控哪些指标？如何建立告警体系？",
    # 前沿探索
    "Test-Time Training的核心思想是什么？为什么推理时还能学习？",
    "World Model在Agent规划中的作用：Dreamer系列论文的核心贡献。",
    "Multi-Agent系统如何避免通信爆炸？讨论消息路由和共识算法。",
    "LLM自对弈(Self-Play)的数据飞轮：SPIN、Self-Rewarding等方法对比。",
    "量子计算对AI的潜在影响：哪些算法任务可能被加速？",
]

if __name__ == "__main__":
    import random
    
    print("""
╔══════════════════════════════════════════════════════╗
║     PHOENIX MONSTER v3 — 百轮自进化                  ║
║     300+ 论文 → 洞察提取 → 策略进化 → 100轮求解       ║
╚══════════════════════════════════════════════════════╝
""")
    
    # Phase 1: 采集论文
    collector = PaperCollector()
    papers = collector.fetch(max_per_query=20)
    print(f"\n✅ 采集: {len(papers)} 篇论文")
    
    # Phase 2: 论文反思
    reflector = PaperReflector()
    insights = reflector.reflect_batch(papers, batch_size=15)
    print(f"\n✅ 反思: {len(insights)} 条洞察")
    print(f"   分布: {dict(reflector.categories.most_common())}")
    
    # Phase 3: 进化引擎初始化
    engine = EvolutionEngine()
    engine.incorporate_insights(insights)
    print(f"\n✅ 初始化策略权重: {json.dumps({k:round(v,3) for k,v in engine.weights.items()}, ensure_ascii=False)}")
    
    # Phase 4: 百轮进化
    print(f"\n{'='*60}")
    print(f"🔄 PHASE 4: 百轮进化 — {len(TASK_BANK)} 个任务 × 循环")
    print(f"{'='*60}")
    
    start_time = time.time()
    milestone_interval = 20
    
    for round_num in range(100):
        record = engine.run_evolution_round(TASK_BANK, round_num)
        
        # 每10轮显示进度
        if (round_num + 1) % 10 == 0 or round_num == 0:
            elapsed = time.time() - start_time
            print(f"\n  📊 第{round_num+1:3d}轮 | 均分:{engine.total_score/(round_num+1):.3f} | "
                  f"最优策略:{max(engine.weights,key=engine.weights.get)} | "
                  f"耗时:{elapsed:.0f}s | 调用:{engine.total_calls}")
        
        # 每20轮重新喂论文洞察（持续学习）
        if (round_num + 1) % milestone_interval == 0 and round_num > 0:
            print(f"\n  📖 第{round_num+1}轮: 重新摄入论文洞察...")
            engine.incorporate_insights(insights)
        
        # 极慢速避免API限流
        time.sleep(1)
    
    elapsed = time.time() - start_time
    
    # ═══════════════════════════════════
    # 最终报告
    # ═══════════════════════════════════
    final_avg = engine.total_score / 100
    first_20_avg = sum(r["score"] for r in engine.evolution_history[:20]) / 20
    last_20_avg = sum(r["score"] for r in engine.evolution_history[-20:]) / 20
    ttrl_gain = last_20_avg - first_20_avg
    
    print(f"\n{'='*60}")
    print(f"🏆 PHOENIX MONSTER v3 — 百轮进化完成")
    print(f"{'='*60}")
    print(f"   论文阅读:     {len(papers)} 篇")
    print(f"   提取洞察:     {len(insights)} 条")
    print(f"   进化轮数:     100 轮")
    print(f"   总LLM调用:    {engine.total_calls} 次")
    print(f"   总耗时:       {elapsed:.0f}s ({elapsed/60:.1f}分)")
    print(f"")
    print(f"   最终均分:     {final_avg:.3f}")
    print(f"   前20轮均分:   {first_20_avg:.3f}")
    print(f"   后20轮均分:   {last_20_avg:.3f}")
    print(f"   TTRL进化增益: {ttrl_gain:+.3f} ({ttrl_gain*100:+.1f}%)")
    print(f"")
    print(f"   最终策略排名:")
    for k, v in sorted(engine.weights.items(), key=lambda x: -x[1]):
        bar = "█" * int(v * 80)
        print(f"     {k:20s} {v:.3f} {bar}")
    print(f"")
    print(f"   被淘汰策略: {min(engine.weights, key=engine.weights.get)}")
    print(f"   最优策略:   {max(engine.weights, key=engine.weights.get)}")
    print(f"{'='*60}")
    
    # 保存
    os.makedirs("experiments", exist_ok=True)
    report = {
        "version": "Phoenix Monster v3",
        "timestamp": datetime.now().isoformat(),
        "papers_collected": len(papers),
        "insights_extracted": len(insights),
        "insight_categories": dict(reflector.categories.most_common()),
        "evolution_rounds": 100,
        "total_llm_calls": engine.total_calls,
        "total_time_seconds": elapsed,
        "final_avg_score": round(final_avg, 3),
        "TTRL_gain": round(ttrl_gain, 3),
        "final_strategy_weights": {k: round(v, 3) for k, v in engine.weights.items()},
        "evolution_history": engine.evolution_history,
    }
    
    filename = f"experiments/phoenix_v3_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n💾 报告: {filename}")
    print("✅ PHOENIX MONSTER v3 COMPLETE.")
