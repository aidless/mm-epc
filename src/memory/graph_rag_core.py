# src/memory/graph_rag_core.py

import networkx as nx


class GraphMemory:
    """
    简易版 GraphRAG 记忆系统
    
    结构：节点代表事件/实体，边代表关系。
    """
    def __init__(self):
        self.graph = nx.Graph()
        self.node_id_counter = 0
    
    def ingest_event(self, event_text: str, source_node: str):
        """将新经验转化为图谱结构"""
        # 1. 提取关键词作为节点 (简化实现)
        nodes = set(event_text.lower().split())
        self.graph.add_nodes_from(nodes)
        
        # 2. 建立与源节点的关联
        if source_node:
            for node in nodes:
                self.graph.add_edge(source_node, node)
        
        print(f"🧠 已存入图谱：连接到 {source_node}")
    
    def query_global_summary(self, query_keywords: list):
        """
        跨节点全局检索（这是 GraphRAG 的核心杀手锏）
        """
        results = []
        for kw in query_keywords:
            neighbors = list(self.graph.neighbors(kw))
            results.extend(neighbors)
        
        # 返回连通度高的节点
        unique_results = list(set(results))
        return unique_results


# 集成示例
memory = GraphMemory()
memory.ingest_event("User searched for iPhone 15", "session_001")
memory.ingest_event("Viewed item price $1000", "session_001")

summary = memory.query_global_summary(["iPhone"])
print(f"📊 全局总结检索结果: {summary}")