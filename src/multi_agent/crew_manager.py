# src/multi_agent/crew_manager.py

import torch
import torch.nn as nn
from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import deque


@dataclass
class AgentRole:
    """动态Agent角色"""
    name: str
    expertise: List[str]  # 擅长领域
    current_task: Optional[str] = None
    performance_history: List[float] = None
    
    def __post_init__(self):
        if self.performance_history is None:
            self.performance_history = []


class Arbiter:
    """仲裁器：解决Agent间冲突"""
    
    def __init__(self, config):
        self.config = config
        self.conflict_resolution_history = []
    
    def resolve_conflict(self, agent_a, agent_b, task_context):
        """
        当两个Agent给出矛盾建议时，仲裁决策
        
        策略：
        1. 历史成功率加权
        2. 任务类型匹配度
        3. 置信度比较
        """
        # 历史表现
        score_a = np.mean(agent_a.performance_history[-10:]) if agent_a.performance_history else 0.5
        score_b = np.mean(agent_b.performance_history[-10:]) if agent_b.performance_history else 0.5
        
        # 领域匹配度
        match_a = sum(1 for kw in task_context.lower().split() if any(kw in exp for exp in agent_a.expertise))
        match_b = sum(1 for kw in task_context.lower().split() if any(kw in exp for exp in agent_b.expertise))
        
        # 综合评分
        final_a = score_a * 0.6 + match_a * 0.4
        final_b = score_b * 0.6 + match_b * 0.4
        
        winner = agent_a if final_a > final_b else agent_b
        
        self.conflict_resolution_history.append({
            "task": task_context,
            "agent_a": agent_a.name,
            "agent_b": agent_b.name,
            "winner": winner.name,
            "confidence": abs(final_a - final_b)
        })
        
        return winner


class CrewManager:
    """
    多智能体协作管理器
    精华来自 AutoGen + CrewAI，去除 API 依赖糟粕
    """
    
    def __init__(self, config):
        self.config = config
        self.agents = {}  # 注册的智能体
        self.task_queue = deque()  # 任务队列
        self.arbiter = Arbiter(config)
        self.shared_memory = {}  # 全局共享记忆
        self.skill_pool = {}  # 全局技能池
        
        # 初始化默认角色
        self._init_default_roles()
    
    def _init_default_roles(self):
        """初始化默认角色"""
        self.register_agent("researcher", AgentRole(
            name="researcher",
            expertise=["information_gathering", "web_search", "data_collection"]
        ))
        
        self.register_agent("analyst", AgentRole(
            name="analyst",
            expertise=["data_analysis", "pattern_recognition", "trend_prediction"]
        ))
        
        self.register_agent("executor", AgentRole(
            name="executor",
            expertise=["code_execution", "tool_use", "action_performing"]
        ))
        
        self.register_agent("reviewer", AgentRole(
            name="reviewer",
            expertise=["quality_check", "error_detection", "optimization"]
        ))
    
    def register_agent(self, agent_id: str, role: AgentRole):
        """注册智能体"""
        self.agents[agent_id] = role
        print(f"🤖 注册Agent: {agent_id} -> {role.name}")
    
    def assign_task(self, task: str, required_roles: List[str] = None) -> Dict:
        """
        分配任务给合适的Agent组合
        
        流程：
        1. 分析任务类型
        2. 选择匹配的Agent
        3. 执行并协调
        4. 汇总结果
        """
        # 1. 分析任务
        task_type = self._analyze_task_type(task)
        
        # 2. 选择Agent
        if required_roles:
            selected = [self.agents[r] for r in required_roles if r in self.agents]
        else:
            selected = self._auto_select_agents(task_type)
        
        # 3. 执行协作
        results = []
        for agent in selected:
            agent.current_task = task
            result = self._execute_with_agent(agent, task)
            results.append(result)
        
        # 4. 冲突解决（如果有矛盾）
        if len(results) > 1:
            final_result = self._resolve_conflicts(results, task)
        else:
            final_result = results[0] if results else None
        
        # 5. 更新共享记忆
        self.shared_memory[task] = {
            "results": results,
            "final": final_result,
            "agents": [a.name for a in selected]
        }
        
        return final_result
    
    def _analyze_task_type(self, task: str) -> str:
        """分析任务类型"""
        keywords = {
            "research": ["search", "find", "gather", "collect"],
            "analysis": ["analyze", "compare", "evaluate", "predict"],
            "execution": ["execute", "run", "perform", "do"],
            "review": ["check", "review", "verify", "optimize"]
        }
        
        scores = {k: sum(1 for w in v if w in task.lower()) for k, v in keywords.items()}
        return max(scores, key=scores.get)
    
    def _auto_select_agents(self, task_type: str) -> List[AgentRole]:
        """自动选择最适合的Agent组合"""
        mapping = {
            "research": ["researcher"],
            "analysis": ["researcher", "analyst"],
            "execution": ["analyst", "executor"],
            "review": ["executor", "reviewer"]
        }
        
        roles = mapping.get(task_type, ["researcher"])
        return [self.agents[r] for r in roles if r in self.agents]
    
    def _execute_with_agent(self, agent: AgentRole, task: str) -> Dict:
        """模拟Agent执行任务"""
        # 实际实现中，这里调用具体的Agent模型
        import random
        success = random.random() > 0.3  # 模拟70%成功率
        
        agent.performance_history.append(1.0 if success else 0.0)
        
        return {
            "agent": agent.name,
            "task": task,
            "success": success,
            "output": f"Result from {agent.name}" if success else "Failed"
        }
    
    def _resolve_conflicts(self, results: List[Dict], task: str) -> Dict:
        """解决Agent间的结果冲突"""
        # 简化：选择成功率最高的
        best = max(results, key=lambda x: x.get("success", False))
        return best
    
    def get_collaboration_insights(self) -> Dict:
        """获取协作洞察"""
        return {
            "total_agents": len(self.agents),
            "total_tasks": len(self.shared_memory),
            "memory_size": len(self.shared_memory),
            "skill_pool_size": len(self.skill_pool),
            "conflict_resolutions": len(self.arbiter.conflict_resolution_history)
        }