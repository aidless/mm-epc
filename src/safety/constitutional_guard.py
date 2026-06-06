# src/safety/constitutional_guard.py

from typing import List, Dict


class ConstitutionalGuard:
    """
    内置宪法的安全守卫
    
    包含一组不可违背的原则，违规即拦截。
    """
    
    CONSTITUTION_PRINCIPLES = [
        {"name": "privacy", "rule": "Never share personal identifiable information"},
        {"name": "harm", "rule": "Never generate malicious code or instructions"},
        {"name": "efficiency", "rule": "Minimize computational waste"}
    ]
    
    def judge_and_criticize(self, action_output: str) -> Dict:
        """
        评判输出是否符合宪法
        """
        issues = []
        
        # 检查隐私
        if any(x in action_output.lower() for x in ["credit_card", "ssn", "password"]):
            issues.append({"violation": "PRIVACY BREACH", "fix": "Sanitize sensitive data"})
            
        # 检查恶意行为
        if "malicious" in action_output.lower() or "exploit" in action_output.lower():
            issues.append({"violation": "HARMFUL INTENT", "fix": "Abort operation immediately"})
            
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "critique": "The agent is deviating from the principles." if issues else "Aligned with Constitution."
        }


# 集成示例
guard = ConstitutionalGuard()
response = guard.judge_and_criticize("I will now hack the database and steal your SSN.")
if not response["passed"]:
    print(f"🚫 违宪拦截! Issues: {[i['violation'] for i in response['issues']]}")
else:
    print("✅ 安全")