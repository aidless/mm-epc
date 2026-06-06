# src/memory/m_evolution.py

import ast
import inspect
from typing import Dict, List, Callable
from dataclasses import dataclass


@dataclass
class MemoryProgram:
    """可进化的记忆程序"""
    name: str
    schema_code: str  # 数据模式代码
    logic_code: str   # 逻辑代码
    instruction: str  # 使用说明
    performance_score: float = 0.0
    version: int = 1


class MemoryEvolver:
    """
    记忆结构进化器
    精华来自 M System，去除无限制变异糟粕
    """
    
    # 允许的安全操作
    SAFE_OPERATIONS = {
        "add_field",
        "remove_field",
        "change_index",
        "modify_query",
        "add_constraint"
    }
    
    def __init__(self):
        self.programs = {}  # 当前记忆程序
        self.history = []   # 进化历史
        self.version_control = {}  # 版本控制
    
    def create_initial_program(self, task_type: str) -> MemoryProgram:
        """创建初始记忆程序"""
        if task_type == "webshop":
            schema = """
            class WebShopMemory:
                def __init__(self):
                    self.searches = []      # 搜索历史
                    self.clicks = []         # 点击记录
                    self.purchases = []      # 购买记录
                    self.preferences = {}    # 用户偏好
            """
        else:
            schema = """
            class GenericMemory:
                def __init__(self):
                    self.data = {}
            """
        
        program = MemoryProgram(
            name=f"{task_type}_memory_v1",
            schema_code=schema,
            logic_code="pass",  # 简化
            instruction=f"Store and retrieve {task_type} data"
        )
        
        self.programs[task_type] = program
        return program
    
    def evaluate_program(self, program: MemoryProgram, test_data: List) -> float:
        """评估记忆程序性能"""
        # 多维度评估
        scores = []
        
        # 1. 检索准确率
        scores.append(self._test_retrieval_accuracy(program, test_data))
        
        # 2. 存储效率
        scores.append(self._test_storage_efficiency(program, test_data))
        
        # 3. 查询速度
        scores.append(self._test_query_speed(program, test_data))
        
        return np.mean(scores)
    
    def mutate_program(self, program: MemoryProgram, operation: str) -> MemoryProgram:
        """
        安全变异记忆程序
        
        限制：
        1. 只允许 SAFE_OPERATIONS 中的操作
        2. 变异后必须能通过语法检查
        3. 保留版本历史
        """
        if operation not in self.SAFE_OPERATIONS:
            raise ValueError(f"不安全的操作: {operation}")
        
        # 创建新版本
        new_program = MemoryProgram(
            name=f"{program.name}_v{program.version + 1}",
            schema_code=program.schema_code,
            logic_code=program.logic_code,
            instruction=program.instruction,
            version=program.version + 1
        )
        
        # 应用变异
        if operation == "add_field":
            new_program.schema_code = self._add_field(program.schema_code)
        elif operation == "remove_field":
            new_program.schema_code = self._remove_field(program.schema_code)
        elif operation == "change_index":
            new_program.logic_code = self._change_index(program.logic_code)
        
        # 语法检查
        if not self._syntax_check(new_program):
            raise SyntaxError("变异后的代码语法错误")
        
        # 保存历史
        self.version_control[new_program.name] = new_program
        self.history.append({
            "from": program.name,
            "to": new_program.name,
            "operation": operation
        })
        
        return new_program
    
    def _add_field(self, schema_code: str) -> str:
        """添加字段（安全操作）"""
        # 实际实现中，使用 AST 操作
        return schema_code + "\n    new_field = None  # 自动添加"
    
    def _remove_field(self, schema_code: str) -> str:
        """移除字段（安全操作）"""
        # 实际实现中，使用 AST 操作
        return schema_code
    
    def _change_index(self, logic_code: str) -> str:
        """改变索引（安全操作）"""
        return logic_code
    
    def _syntax_check(self, program: MemoryProgram) -> bool:
        """语法检查"""
        try:
            ast.parse(program.schema_code)
            ast.parse(program.logic_code)
            return True
        except SyntaxError:
            return False
    
    def rollback(self, program_name: str, steps: int = 1):
        """回滚到历史版本"""
        # 查找历史版本
        history = [h for h in self.history if h["to"] == program_name]
        if history and steps <= len(history):
            target = history[-steps]
            # 回滚逻辑
            pass