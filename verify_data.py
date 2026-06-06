"""
自检脚本：读实验输出 JSON，验证数据完整性
防止 "0轮完成但声称成功" 的问题
"""
import json, os, sys

def verify_experiment(path):
    """检查实验输出是否真实有效"""
    issues = []
    
    if not os.path.exists(path):
        return [f"文件不存在: {path}"]
    
    try:
        with open(path, encoding='utf-8-sig') as f:
            data = json.load(f)
    except:
        try:
            with open(path, encoding='gbk') as f:
                data = json.load(f)
        except:
            return [f"JSON 解析失败: {path}"]
    
    # 检查1：有实际轮次 (兼容多种字段名)
    rounds = data.get("rounds", data.get("rounds_completed", 
              data.get("total_llm_calls", 0)))
    # 如果顶层没有，可能在嵌套里
    if rounds == 0 and "raw_results" in data:
        rounds = len(data["raw_results"])
    if rounds == 0:
        issues.append("⚠️  0 轮完成——所有调用可能静默失败")
        return issues
    
    # 检查2：有权重数据 (兼容多种嵌套位置)
    weights = data.get("weights", data.get("final_weights", 
              data.get("w_T_pure", {})))
    if not weights and "raw_results" in data:
        # Phase 3 bootstrap format
        weights = {}
    if not weights and "w_T_pure" in data:
        weights = data["w_T_pure"]
    
    if weights:
        wv = list(weights.values())
        # 检查3：权重不是全均匀（说明有进化）
        if len(wv) > 0 and max(wv) == min(wv):
            issues.append("⚠️  所有权重相同——TTRL 未生效")
        # 检查4：权重和为1
        if len(wv) > 0 and abs(sum(wv) - 1.0) > 0.01:
            issues.append(f"⚠️  权重和={sum(wv):.3f}，应为1.0")
    
    # 检查5：PCI 合理范围
    pci = data.get("pci", 0)
    if pci == 0 and rounds > 0:
        issues.append("⚠️  PCI=0 但有轮次数据——可能为默认值")
    
    # 检查6：耗时合理
    t = data.get("time", 0)
    if t < 1 and rounds > 0:
        issues.append(f"⚠️  耗时仅 {t}s 但完成 {rounds} 轮——不可能")
    
    return issues

# 检查所有实验数据
base = "/mnt/c/Users/Administrator/Desktop/aettl-research/experiments"
all_ok = True
for f in sorted(os.listdir(base)):
    if f.endswith(".json") and f.startswith("mm_epc"):
        path = os.path.join(base, f)
        issues = verify_experiment(path)
        if issues:
            print(f"❌ {f}")
            for i in issues:
                print(f"   {i}")
            all_ok = False
        else:
            print(f"✅ {f}")

if all_ok:
    print("\n全部实验数据通过验证")
else:
    print(f"\n⚠️  发现问题，需要重新运行")
