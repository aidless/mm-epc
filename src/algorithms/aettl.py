import sys
import os
import json

# 自动修复路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
sys.path.insert(0, project_root)
os.chdir(project_root) # 切换到项目根目录，防止路径混乱

from src.environments.webshop_env import MiniWebShopEnv

class AgentRunner:
    def __init__(self):
        print("🧠 初始化 Agent...")
        self.env = MiniWebShopEnv()

    def run_task(self, task_id=0):
        obs = self.env.reset()
        print(f"\n🎯 任务 {task_id}: 购买 '{self.env.task['query']}'")
        
        trajectory = []
        step = 0
        
        while not self.env.done and step < 10:
            # 1. 简单策略 (Rule-based)
            state = self.env.state
            if state == "start": action = f"search[{self.env.task['query']}]"
            elif state == "list": action = "click[Item_C]"
            elif state == "detail": action = "buy"
            elif state == "cart": action = "submit"
            else: action = "noop"

            # 2. 执行并记录
            next_obs, reward, done, info = self.env.step(action)
            trajectory.append({
                "step": step,
                "state": state,
                "action": action,
                "reward": reward
            })
            print(f"   步骤 {step}: [{state}] -> 动作: {action} -> 奖励: {reward}")
            step += 1

        return trajectory

    def run_all(self, num_tasks=3):
        all_data = []
        for i in range(num_tasks):
            traj = self.run_task(i)
            all_data.append(traj)
            
        # 💾 关键步骤：确保数据写入
        save_path = "experiments/agent_trajectories.json"
        os.makedirs("experiments", exist_ok=True)
        
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4)
            
        print(f"\n💾 数据已成功保存到: {save_path}")
        return all_data

if __name__ == "__main__":
    runner = AgentRunner()
    runner.run_all()
