# src/spacetime/st_engine.py

import torch.nn as nn


class SWTTransformer(nn.Module):
    """
    时空扭曲变换器：
    引入度规张量g_μν模拟引力场对信息流的影响
    """
    def __init__(self, embed_dim=128, num_heads=8):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        
        # 曲率参数λ ∈ (-∞,+∞)，负值对应黑洞奇点
        self.curvature = nn.Parameter(torch.zeros(1))
        
        self.query_proj = nn.Linear(embed_dim, embed_dim)
        self.key_proj = nn.Linear(embed_dim, embed_dim)
        self.value_proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, x):
        B, S, D = x.size()
        
        Q = self.query_proj(x).view(B, S, self.num_heads, D//self.num_heads)
        K = self.key_proj(x).view(B, S, self.num_heads, D//self.num_heads)
        V = self.value_proj(x).view(B, S, self.num_heads, D//self.num_heads)
        
        # 时空曲率调整注意力权重
        attn_weights = torch.einsum("bqhd,bkhd->bhqk", Q, K) / math.sqrt(D)
        curvature_factor = torch.tanh(self.curvature)
        adjusted_weights = attn_weights * (1 + curvature_factor)
        
        context = torch.matmul(F.softmax(adjusted_weights, dim=-1), V)
        return context.view(B, S, D)