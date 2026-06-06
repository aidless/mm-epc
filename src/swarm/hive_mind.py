# src/swarm/hive_mind.py

import networkx as nx


class SwarmNode:
    """
    具有社会性行为的分布式节点
    
    它不仅能学习，还能“传染”经验给邻居节点。
    """
    def __init__(self, node_id, local_policy):
        self.node_id = node_id
        self.policy = local_policy
        self.knowledge_spread = set() # 传播的知识标签
        self.neighbors = []           # 社交网络
    
    def encounter_neighbor(self, other_node):
        """
        遇到邻居节点时的信息交换（类似蚂蚁的信息素交换）
        """
        shared_knowledge = self.knowledge_spread & other_node.knowledge_spread
        
        if len(shared_knowledge) > 0:
            print(f"🤝 Node {self.node_id} 与 Node {other_node.node_id} 达成共识：{shared_knowledge}")
            
            # 关键：双向同步权重
            # 在现实中，这可以通过 P2P 网络或区块链实现
            return {"merged": True, "new_strategy": f"Mixed_{self.node_id}_{other_node.node_id}"}
        return {"merged": False}


class HiveMindOrchestrator:
    """
    无中心化管理器
    
    没有上帝视角，只有局部的连接。
    """
    def __init__(self, n_nodes):
        self.graph = nx.Graph()
        for i in range(n_nodes):
            node = SwarmNode(i, "SimplePolicy_v1")
            self.graph.add_node(node.node_id, data=node)
        
        # 形成随机网状结构
        for u, v in list(nx.connected_components(self.graph))[-1]: 
             pass # 实际中这里建立邻居关系
            
    def trigger_emergence(self):
        print("🌍 正在构建去中心化蜂巢网络...")
        nodes = list(self.graph.nodes())
        # 模拟大规模并发下的局部交互
        for _ in range(10):
            a, b = nodes[0], nodes[-1]
            result = self.graph.nodes[a]['data'].encounter_neighbor(self.graph.nodes[b]['data'])
            if result["merged"]:
                print(f"✨ 涌现奇迹：新策略产生！全局鲁棒性提升。")