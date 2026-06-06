# src/a2a/phoenix_a2a_bridge.py

import json
import uuid
from typing import Dict, List, Optional


class PhoenixA2ABridge:
    """
    Phoenix Monster 的 Agent-to-Agent 桥接层
    
    能力：
    1. 能力广播 (Capability Broadcast)
    2. Agent 发现 (Agent Discovery)
    3. 任务委托 (Task Delegation)
    4. 异构协议翻译 (Protocol Translation)
    """
    
    def __init__(self, agent_id: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.discovered_agents = {}  # 发现的远方 Agent
        self.active_tasks = {}       # 当前委托的任务
        
    def broadcast_capabilities(self) -> Dict:
        """
        广播自身能力给其他 Agent
        """
        return {
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "protocol_version": "phoenix-a2a-v1",
            "endpoint": f"phoenix://{self.agent_id}/invoke"
        }
    
    def discover_agent(self, capability_request: str) -> Optional[Dict]:
        """
        发现具有特定能力的远方 Agent
        
        Args:
            capability_request: 需要的技能，如 "quantum_computing"
        """
        for agent_id, info in self.discovered_agents.items():
            if capability_request in info.get("capabilities", []):
                return {"agent_id": agent_id, **info}
        return None
    
    def delegate_task(self, target_agent_id: str, task: str) -> str:
        """
        委派任务给其他 Agent
        
        Args:
            target_agent_id: 目标 Agent ID
            task: 任务描述
            
        Returns:
            task_id: 任务追踪 ID
        """
        task_id = str(uuid.uuid4())[:8]
        
        self.active_tasks[task_id] = {
            "target": target_agent_id,
            "task": task,
            "status": "pending",
            "result": None
        }
        
        print(f"📤 Agent {self.agent_id} → Agent {target_agent_id}")
        print(f"   任务: {task}")
        print(f"   ID: {task_id}")
        
        return task_id
    
    def receive_result(self, task_id: str, result: any):
        """接收远方 Agent 返回的结果"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["result"] = result
            print(f"📥 Agent {self.agent_id} 收到结果: {task_id} = {result}")
    
    def translate_protocol(self, raw_message: str, source_format: str) -> Dict:
        """
        协议翻译：将不同 Agent 的消息格式统一
        
        支持格式：OpenAI, Anthropic, Google A2A, 本地模型
        """
        if source_format == "openai":
            return {"content": raw_message, "format": "phoenix-internal"}
        elif source_format == "anthropic":
            return {"content": raw_message, "format": "phoenix-internal"}
        elif source_format == "google-a2a":
            # 原生 A2A 格式直接解析
            return json.loads(raw_message)
        else:
            return {"content": raw_message, "format": "phoenix-internal", "warning": "未知格式，使用原始文本"}


# === 集成示例 ===
bridge = PhoenixA2ABridge(
    agent_id="phoenix-monster-001",
    capabilities=["quantum_cognition", "swarm_intelligence", "world_modeling", "neuromorphic_computing"]
)

# 广播能力
caps = bridge.broadcast_capabilities()
print(f"📡 广播能力: {caps['capabilities']}")

# 委托量子计算任务
task_id = bridge.delegate_task("quantum-agent-007", "optimize_shors_algorithm")
bridge.receive_result(task_id, {"qbits_used": 1024, "speedup": "10^6x"})