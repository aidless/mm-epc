# src/embodied/simulator_adapter.py

class PhysicsWorldAdapter:
    """
    物理世界适配器 (类似简化的 Isaac Gym/PyBullet)
    
    功能：管理 Agent 的物理状态反馈，支持重力、摩擦力等参数。
    """
    def __init__(self, gravity=9.81, friction=0.5):
        self.gravity = gravity
        self.friction = friction
        self.object_positions = {} # 记录桌上物体位置
    
    def set_object_position(self, obj_id, pos_3d):
        """更新环境中物体的位置"""
        self.object_positions[obj_id] = pos_3d
        print(f"🌍 已将 {obj_id} 放置在三维空间：{pos_3d}")
    
    def step(self, action, dt=0.01):
        """
        执行一步物理仿真
        :param action: 机械臂位移 [dx, dy, dz]
        :returns: next_observation, reward, done
        """
        # 简单的动力学积分计算
        current_pos = list(action) 
        next_pos = [x + dx * dt for dx, x in zip(action, current_pos)]
        
        # 碰撞检测模拟
        collision_penalty = 0.0
        if abs(next_pos[2]) < 0.05: # 撞桌子了
            collision_penalty = -5.0
            
        reward = -sum(abs(x) for x in next_pos) + collision_penalty
        return next_pos, reward, False


# === 集成示例 ===
sim = PhysicsWorldAdapter()
action_step = [0.1, 0.0, 0.0] # 向右推一下
new_pos, rew, is_done = sim.step(action_step)
print(f"💡 物理反馈：奖励={rew}, 当前位置={new_pos}")