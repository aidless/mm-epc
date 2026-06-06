# src/coding/swe_agent_loop.py

class SWEAgentLoop:
    """
    OpenHands 核心的 IDE Loop 简化版
    
    功能：让 Agent 尝试执行一个动作，如果失败，根据 Error Log 重新生成动作。
    """
    def __init__(self):
        self.error_memory = [] # 记录历史错误以避免重复犯错
    
    def optimize_action(self, task_description, current_solution, error_log=None):
        """
        基于反馈的自我修复迭代
        
        Args:
            error_log: str, 上一次执行的报错信息
        Returns:
            dict: {"solution": ..., "status": "success" | "retry"}
        """
        print(f"🔍 正在分析 {task_description}...")
        
        # 1. 尝试当前方案 (模拟)
        success_rate = np.random.uniform(0, 1)
        
        if success_rate > 0.8:
            return {"solution": current_solution, "status": "success", "reward": 1.0}
        
        # 2. 如果没有成功且有报错，进入自我修复
        if error_log:
            print(f"⛔ 捕获异常: {error_log}")
            self.error_memory.append(error_log)
            
            # 核心优化：使用历史错误知识库来指导重试
            if len(self.error_memory) > 0:
                advice = f"避免上次犯过的错误：{self.error_memory[-1]}"
                # 实际场景中这里会调用 LLM 根据 advice 重新生成代码/动作
                print(f"💡 引入知识注入: {advice}")
                
            # 模拟重试后的成功率提升
            retry_success_rate = np.random.uniform(0, 1)
            if retry_success_rate > 0.9:
                return {"solution": f"Fixed: {current_solution}", "status": "success", "reward": 0.9}
        
        return {"solution": current_solution, "status": "retry", "reward": 0.0}


# 集成示例
loop = SWEAgentLoop()
res = loop.optimize_action("Login feature", "login_func()", error_log="TypeError: undefined variable 'db'")
print(f"最终状态: {res['status']}")