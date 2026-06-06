# src/neuro/chip_edge_logic.py

import time

class LeakyIntegrateFireNeuron:
    """
    简化版生物神经元模型 (LIF Model)
    
    功能：
    1. 积分 (Integrate): 收集输入信号增加电位
    2. 泄漏 (Leak): 忘记无关紧要的信号防止过载
    3. 发放 (Fire): 达到阈值后发送脉冲信号
    """
    def __init__(self, threshold=1.0, decay_rate=0.9):
        self.potential = 0.0
        self.threshold = threshold
        self.decay_rate = decay_rate
        self.fired_in_last_ms = 0 # 绝对不应期（休息一下再想事）
    
    def input_signal(self, value):
        """接收外界刺激"""
        self.potential += value
        
    def update(self):
        """
        每一步都更新自身的生物状态
        """
        # 泄漏：逐渐遗忘旧的情绪
        self.potential *= self.decay_rate
        
        # 检查是否该“放电”了
        if self.potential >= self.threshold:
            self.potential -= self.threshold # 重置电位
            self._emit_spike()
            return True # 产生了动作
        return False
    
    def _emit_spike(self):
        print("⚡ SPARK! (Neuron Fired)")


class SiliconBrainChip:
    """
    模拟神经形态芯片的边缘计算控制器
    
    它不是在算矩阵乘法，而是在管理数千个神经元的火花。
    """
    def __init__(self):
        # 初始化一个小型的神经网络簇
        self.input_layer = [LeakyIntegrateFireNeuron(1.0) for _ in range(5)]
        self.output_layer = LeakyIntegrateFireNeuron(5.0) # 输出层需要更多刺激才激活
        print("🔬 Silicon Brain Initialized on Edge Chip (voltage: 1.5V)")
    
    def sensory_cycle(self):
        """
        感觉循环：感知 -> 冲动 -> 行动
        
        这是真正的高效计算，不需要占用 100% 的算力。
        """
        # 模拟外部传感器传来的微弱信号
        inputs = [0.2, 0.1, 0.3, 0.4, 0.0] 
        
        for neuron, inp in zip(self.input_layer, inputs):
            neuron.input_signal(inp)
            if neuron.update():
                # 如果输入层有脉冲爆发，传递给输出层
                self.output_layer.input_signal(1.0)
                
        # 最终决策
        if self.output_layer.update():
            return "EXECUTE COMMAND: MOVE LEFT!"
        else:
            return "WAITING FOR STRONGER SIGNAL..."


# === 集成示例 ===
chip = SiliconBrainChip()
# 这一轮非常安静，因为刺激不够强
print(chip.sensory_cycle()) 

# 第二轮刺激增强，触发思维火花
chip.input_layer[0].input_signal(2.0) # 强行注入高压电流
print(chip.sensory_cycle())