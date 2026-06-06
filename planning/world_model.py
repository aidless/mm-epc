# src/planning/world_model.py
import torch
import torch.nn as nn


class WorldModel(nn.Module):
    """
    简化的世界模型：预测当前动作导致的下一个状态奖励
    
    功能：作为 TTRL 的“过滤器”，在更新参数前先预测收益。
    """
    def __init__(self, input_dim=128, hidden_dim=256, action_dim=10):
        super().__init__()
        
        # 状态转移网络：输入(当前状态 + 动作) -> 预测(下一步状态 + 奖励)
        self.trans_net = nn.Sequential(
            nn.Linear(input_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        self.reward_head = nn.Linear(hidden_dim, 1)  # 预测奖励
        
    def predict(self, state_t, action_t):
        """
        联合编码状态和动作，预测未来收益
        """
        combined = torch.cat([state_t, action_t], dim=-1)
        x = self.trans_net(combined)
        pred_reward = self.reward_head(x).squeeze(-1)
        return pred_reward
    
    def learn_world(self, traj_data):
        """离线学习世界模型：最小化预测误差"""
        # 这里可以接入真实的交互轨迹进行预训练
        pass


class PlannerGuard:
    """
    基于世界模型的规划守卫
    
    原理：在 Agent 执行动作前，先用世界模型预测该动作是否会导致 Reward > threshold。
    """
    def __init__(self, world_model: WorldModel):
        self.model = world_model
    
    def filter_action(self, state, candidate_actions):
        """过滤掉可能带来负面反馈的动作"""
        filtered = []
        for action in candidate_actions:
            action_vec = torch.zeros_like(state[:, :10]) # 占位符向量
            action_vec[:, -1] = float(action)
            
            score = self.model.predict(state, action_vec)
            if score > 0.5: # 假设 0.5 是好动作阈值
                filtered.append((action, score.item()))
        
        # 按预测分数排序，返回最可能的 Top-1
        return max(filtered, key=lambda x: x[1]) if filtered else None