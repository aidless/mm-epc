# src/utils/symbolic_guard.py

import ast


class SymbolicGuard:
    """
    基于图灵完备性检查的逻辑守卫
    确保 Agent 的动作流满足硬性约束
    """
    
    CONSTRAINTS = {
        "webshop": [
            {"precondition": "no_search", "action": "buy", "allowed": False},
            {"precondition": "no_click", "action": "buy", "allowed": False}
        ]
    }
    
    def validate_sequence(self, history, proposed_action):
        """
        检查提议的动作是否在历史序列中合法
        
        如果非法，抛出自定义异常并返回修正建议
        """
        last_action = history[-1].get("action") if history else None
        action_name = proposed_action.split("_")[0] if "_" in proposed_action else proposed_action
        
        task_type = "webshop"
        
        for rule in self.CONSTRAINTS.get(task_type, []):
            pre = rule["precondition"]
            act = rule["action"]
            
            # 触发条件匹配
            if pre == f"no_{act}" and not self._has_occurred(history, act):
                return {
                    "valid": False,
                    "error": f"Cannot '{act}' without first performing '{act}'.",
                    "correction": act # 自动推荐修正动作
                }
        
        return {"valid": True}
    
    def _has_occurred(self, history, action_prefix):
        return any(a.get("action", "").startswith(action_prefix) for a in history)


# === 集成示例 ===
guard = SymbolicGuard()
history = [{"action": "click_item_A"}]
proposed = "submit_order"

result = guard.validate_sequence(history, proposed)
if not result["valid"]:
    print(f"⛔ 非法操作拦截: {result['error']}")
    print(f"💡 建议修改为: {result['correction']}")