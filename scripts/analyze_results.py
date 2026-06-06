import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np

print("🔍 正在分析 Agent 真实实验数据...")

# 1. 读取数据
data_path = "experiments/agent_trajectories.json"
if not os.path.exists(data_path):
    print(f"❌ 错误：找不到 {data_path}。请先运行 src/algorithms/aettl.py 生成数据。")
    exit()

with open(data_path, "r", encoding="utf-8") as f:
    all_trajectories = json.load(f)

print(f"✅ 成功加载 {len(all_trajectories)} 个任务的轨迹数据。")

# 2. 统计指标
success_count = 0
step_counts = []
action_freq = {}

for traj in all_trajectories:
    steps = len(traj)
    step_counts.append(steps)
    
    # 判断成功：最后一步包含 submit
    last_action = traj[-1]["action"] if traj else ""
    if "submit" in last_action.lower():
        success_count += 1
    
    # 统计动作频率
    for step_data in traj:
        act = step_data["action"]
        action_freq[act] = action_freq.get(act, 0) + 1

success_rate = (success_count / len(all_trajectories)) * 100 if len(all_trajectories) > 0 else 0
avg_steps = np.mean(step_counts)

print(f"📊 统计结果：")
print(f"   - 成功率：{success_rate:.1f}%")
print(f"   - 平均步数：{avg_steps:.1f}")

os.makedirs("paper/figures", exist_ok=True)

# 3. 绘图：图 3 - 成功率饼图
plt.figure(figsize=(5, 5))
colors = ['#4CAF50', '#FF5722']
labels = ['Success', 'Failed']
sizes = [success_count, len(all_trajectories)-success_count]
# 如果没有失败数据，就只画成功
if sizes[1] == 0: sizes[1] = 0.01; labels[1] = ''
plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, explode=(0.05, 0))
plt.title("Agent Task Success Rate", fontsize=13)
plt.savefig("paper/figures/figure3_success_rate.png", dpi=300)
print("✅ 已生成: paper/figures/figure3_success_rate.png")

# 4. 绘图：图 4 - 动作分布柱状图
plt.figure(figsize=(8, 4))
actions = list(action_freq.keys())
counts = list(action_freq.values())
plt.bar(actions, counts, color="#3F51B5")
plt.xlabel("Actions Taken", fontsize=11)
plt.ylabel("Frequency", fontsize=11)
plt.title("Distribution of Agent Actions", fontsize=13)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("paper/figures/figure4_actions_dist.png", dpi=300)
print("✅ 已生成: paper/figures/figure4_actions_dist.png")

print("\n🎉 所有分析图表生成完毕！")
