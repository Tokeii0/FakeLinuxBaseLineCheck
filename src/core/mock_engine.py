import os
import re
import subprocess
import tempfile
from typing import Optional, Tuple

from .rule_manager import Rule, RuleManager


class MockEngine:
    """命令模拟引擎，负责根据规则模拟命令执行结果"""
    
    def __init__(self, rule_manager: RuleManager):
        self.rule_manager = rule_manager
    
    def process_command(self, command: str) -> Tuple[str, bool]:
        """
        处理命令并返回模拟结果
        
        Args:
            command: 要处理的命令
            
        Returns:
            Tuple[str, bool]: (命令输出, 是否被模拟)
        """
        # 查找匹配的规则
        rule = self.rule_manager.find_matching_rule(command)
        if not rule:
            return self._execute_real_command(command), False
        
        # 根据规则类型处理命令
        return self._apply_rule(command, rule), True
    
    def _apply_rule(self, command: str, rule: Rule) -> str:
        """应用规则处理命令"""
        if rule.action == 'replace':
            # 直接返回替换输出
            return rule.output
        
        elif rule.action == 'script':
            # 执行自定义脚本
            return self._execute_custom_script(command, rule.script)
        
        elif rule.action == 'filter':
            # 执行命令并过滤输出
            real_output = self._execute_real_command(command)
            
            # 检查条件
            if rule.condition:
                if self._check_condition(real_output, rule.condition):
                    return self._apply_filter(real_output, rule.filter)
                return real_output
            
            # 无条件直接过滤
            return self._apply_filter(real_output, rule.filter)
        
        elif rule.action == 'empty':
            # 返回空输出
            return ""
        
        # 未知动作，执行真实命令
        return self._execute_real_command(command)
    
    def _execute_real_command(self, command: str) -> str:
        """执行真实命令（仅用于测试）"""
        try:
            # 注意：实际环境中可能需要更安全的方式执行命令
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            return process.stdout + (process.stderr if process.stderr else "")
        except subprocess.TimeoutExpired:
            return "命令执行超时"
        except Exception as e:
            return f"命令执行错误: {str(e)}"
    
    def _execute_custom_script(self, command: str, script: str) -> str:
        """执行自定义脚本"""
        try:
            # 创建临时脚本文件
            with tempfile.NamedTemporaryFile(suffix='.sh', delete=False) as temp:
                # 构建脚本内容
                script_content = f"""#!/bin/bash
CMD="{command}"
{script}
"""
                temp.write(script_content.encode('utf-8'))
                temp_path = temp.name
            
            # 设置执行权限
            os.chmod(temp_path, 0o755)
            
            # 执行脚本
            process = subprocess.run(
                ['/bin/bash', temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # 删除临时文件
            os.unlink(temp_path)
            
            return process.stdout + (process.stderr if process.stderr else "")
        except Exception as e:
            return f"脚本执行错误: {str(e)}"
        
    def _check_condition(self, output: str, condition: str) -> bool:
        """检查输出是否满足条件"""
        try:
            # 创建临时脚本文件
            with tempfile.NamedTemporaryFile(suffix='.sh', delete=False) as temp:
                script_content = f"""#!/bin/bash
echo '{output}' | {condition}
"""
                temp.write(script_content.encode('utf-8'))
                temp_path = temp.name
            
            # 设置执行权限
            os.chmod(temp_path, 0o755)
            
            # 执行脚本
            process = subprocess.run(
                ['/bin/bash', temp_path],
                capture_output=True,
                text=True
            )
            
            # 删除临时文件
            os.unlink(temp_path)
            
            # 如果退出码为0，则条件满足
            return process.returncode == 0
        except Exception:
            return False
    
    def _apply_filter(self, output: str, filter_cmd: str) -> str:
        """应用过滤器处理输出"""
        try:
            # 创建临时脚本文件
            with tempfile.NamedTemporaryFile(suffix='.sh', delete=False) as temp:
                script_content = f"""#!/bin/bash
echo '{output}' | {filter_cmd}
"""
                temp.write(script_content.encode('utf-8'))
                temp_path = temp.name
            
            # 设置执行权限
            os.chmod(temp_path, 0o755)
            
            # 执行脚本
            process = subprocess.run(
                ['/bin/bash', temp_path],
                capture_output=True,
                text=True
            )
            
            # 删除临时文件
            os.unlink(temp_path)
            
            return process.stdout
        except Exception as e:
            return f"过滤执行错误: {str(e)}"
    
    def preview_rule(self, command: str, rule: Rule) -> str:
        """预览规则应用效果"""
        # 临时修改规则状态为启用
        original_enabled = rule.enabled
        rule.enabled = True
        
        # 应用规则并获取结果
        result = self._apply_rule(command, rule)
        
        # 恢复原始状态
        rule.enabled = original_enabled
        
        return result
