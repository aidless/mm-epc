# src/memory/ltm_system.py

import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class LongTermMemory:
    """
    持久化长程记忆系统
    
    机制：
    1. 重要性加权存储
    2. 强度衰减曲线 (Ebbinghaus 遗忘曲线)
    3. 多模态检索（时间、语义、情感、重要性）
    """
    
    def __init__(self):
        self.memories = {}  # 记忆存储
        self.decay_rate = 0.1  # 遗忘速率
        
    def store(self, content: str, importance: float, tags: List[str]):
        """
        存储记忆，按照重要性加权
        """
        memory_id = hashlib.md5(content.encode()).hexdigest()[:8]
        
        self.memories[memory_id] = {
            "content": content,
            "importance": importance,  # 0.0 ~ 1.0
            "tags": tags,
            "timestamp": datetime.now(),
            "access_count": 0,
            "last_recalled": datetime.now(),
            "strength": importance  # 记忆强度，随时间和使用改变
        }
        
        print(f"🧠 记忆存储: [{memory_id}] {content[:30]}... (重要度: {importance:.2f})")
        
        return memory_id
    
    def recall(self, query_tags: List[str], time_range: Optional[timedelta] = None) -> List[Dict]:
        """
        多模态检索：
        1. 语义匹配（标签重合度）
        2. 时间过滤
        3. 情感/重要性筛选
        4. 访问频率加权
        """
        candidates = []
        now = datetime.now()
        
        for mem_id, mem in self.memories.items():
            # 时间过滤
            if time_range and (now - mem["timestamp"]) > time_range:
                continue
                
            # 记忆强度衰减
            time_since_last = (now - mem["last_recalled"]).total_seconds()
            mem["strength"] *= (1 - self.decay_rate) ** (time_since_last / 86400)  # 按天衰减
            
            # 标签匹配度
            overlap = len(set(query_tags) & set(mem["tags"]))
            if len(mem["tags"]) > 0:
                match_score = overlap / len(mem["tags"])
            else:
                match_score = 0
            
            # 综合评分
            total_score = (
                0.4 * match_score +          # 标签匹配
                0.3 * mem["importance"] +    # 记忆重要性
                0.2 * mem["strength"] +      # 当前记忆强度
                0.1 * min(mem["access_count"] / 10, 1.0)  # 访问频率
            )
            
            if total_score > 0.1:
                candidates.append({"id": mem_id, "score": total_score, **mem})
        
        # 按评分排序
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # 更新访问记录
        for c in candidates[:3]:
            self.memories[c["id"]]["access_count"] += 1
            self.memories[c["id"]]["last_recalled"] = now
        
        print(f"🔍 检索到 {len(candidates)} 条记忆，返回 Top-{min(3, len(candidates))}")
        return candidates[:3]
    
    def consolidate(self):
        """
        记忆巩固：删除已淡忘的弱记忆
        """
        to_delete = []
        for mem_id, mem in self.memories.items():
            if mem["strength"] < 0.01:
                to_delete.append(mem_id)
        
        for mem_id in to_delete:
            del self.memories[mem_id]
        
        print(f"🧹 记忆整理: 删除了 {len(to_delete)} 条弱记忆，当前剩余 {len(self.memories)} 条")


# === 集成示例 ===
ltm = LongTermMemory()

# 存储关键经验
ltm.store("量子认知层在高温下退相干严重", importance=0.9, tags=["quantum", "hardware", "failure"])
ltm.store("蜂巢共识在 Agent 数 >50 时效率达到峰值", importance=0.8, tags=["swarm", "scaling", "success"])
ltm.store("图记忆在复杂查询时优于向量搜索", importance=0.7, tags=["graphrag", "memory", "comparison"])

# 检索与"量子"、"失败"相关的记忆
results = ltm.recall(query_tags=["quantum", "failure"])
for r in results:
    print(f"  📝 {r['content'][:40]}... (评分: {r['score']:.2f})")

# 记忆整理
ltm.consolidate()