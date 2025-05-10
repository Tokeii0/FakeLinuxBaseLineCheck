import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Set

class Rule:
    """规则类，表示一条命令伪装规则"""
    
    def __init__(self, rule_id: int, name: str, description: str, pattern: str, 
                 action: str, enabled: bool = True, **kwargs):
        self.id = rule_id
        self.name = name
        self.description = description
        self.pattern = pattern
        self.action = action
        self.enabled = enabled
        
        # 根据不同的动作类型，存储相应的数据
        self.output = kwargs.get('output', '')        # replace动作的输出内容
        self.script = kwargs.get('script', '')        # script动作的脚本内容
        self.filter = kwargs.get('filter', '')        # filter动作的过滤命令
        self.condition = kwargs.get('condition', '')  # filter动作的条件
    
    def to_dict(self) -> Dict[str, Any]:
        """将规则转换为字典格式"""
        rule_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'pattern': self.pattern,
            'action': self.action,
            'enabled': self.enabled
        }
        
        # 根据动作类型添加相应的字段
        if self.action == 'replace' and self.output:
            rule_dict['output'] = self.output
        elif self.action == 'script' and self.script:
            rule_dict['script'] = self.script
        elif self.action == 'filter':
            if self.filter:
                rule_dict['filter'] = self.filter
            if self.condition:
                rule_dict['condition'] = self.condition
        
        return rule_dict
    
    @classmethod
    def from_dict(cls, rule_dict: Dict[str, Any]) -> 'Rule':
        """从字典创建规则对象"""
        rule_id = rule_dict.get('id', 0)
        name = rule_dict.get('name', '')
        description = rule_dict.get('description', '')
        pattern = rule_dict.get('pattern', '')
        action = rule_dict.get('action', '')
        enabled = rule_dict.get('enabled', True)
        
        kwargs = {}
        if 'output' in rule_dict:
            kwargs['output'] = rule_dict['output']
        if 'script' in rule_dict:
            kwargs['script'] = rule_dict['script']
        if 'filter' in rule_dict:
            kwargs['filter'] = rule_dict['filter']
        if 'condition' in rule_dict:
            kwargs['condition'] = rule_dict['condition']
        
        return cls(rule_id, name, description, pattern, action, enabled, **kwargs)
    
    def matches(self, command: str) -> bool:
        """检查命令是否匹配规则的模式"""
        if not self.enabled:
            return False
        try:
            pattern = re.compile(self.pattern, re.IGNORECASE)
            return bool(pattern.search(command))
        except re.error:
            return False


class AppConfig:
    """应用程序配置类"""
    
    def __init__(self):
        self.log_directory = "/tmp"
        self.log_filename = "ssh_commands.log"
    
    def get_log_path(self) -> str:
        """获取完整的日志文件路径"""
        return os.path.join(self.log_directory, self.log_filename)
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            "log_directory": self.log_directory,
            "log_filename": self.log_filename
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AppConfig':
        """从字典创建配置对象"""
        config = cls()
        if "log_directory" in config_dict:
            config.log_directory = config_dict["log_directory"]
        if "log_filename" in config_dict:
            config.log_filename = config_dict["log_filename"]
        return config


class RuleManager:
    """规则管理器，负责加载、保存和应用规则"""
    
    def __init__(self):
        self.rules: List[Rule] = []
        self.next_id = 1
        self.config = AppConfig()
    
    def load_rules(self, file_path: Union[str, Path]) -> bool:
        """从文件加载规则和配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.rules = []
            for rule_dict in data.get('rules', []):
                rule = Rule.from_dict(rule_dict)
                self.rules.append(rule)
                
                # 更新next_id为最大ID+1
                if rule.id >= self.next_id:
                    self.next_id = rule.id + 1
            
            # 加载配置
            if 'config' in data:
                self.config = AppConfig.from_dict(data['config'])
            
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"加载规则失败: {str(e)}")
            return False
    
    def save_rules(self, file_path: Union[str, Path]) -> bool:
        """保存规则和配置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            data = {
                'rules': [rule.to_dict() for rule in self.rules],
                'config': self.config.to_dict()
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存规则失败: {str(e)}")
            return False
    
    def add_rule(self, rule: Rule) -> int:
        """添加新规则"""
        if rule.id == 0:
            rule.id = self.next_id
            self.next_id += 1
        
        self.rules.append(rule)
        return rule.id
    
    def update_rule(self, rule: Rule) -> bool:
        """更新现有规则"""
        for i, existing_rule in enumerate(self.rules):
            if existing_rule.id == rule.id:
                self.rules[i] = rule
                return True
        return False
    
    def delete_rule(self, rule_id: int) -> bool:
        """删除规则"""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                del self.rules[i]
                return True
        return False
    
    def get_rule(self, rule_id: int) -> Optional[Rule]:
        """获取特定规则"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def find_matching_rule(self, command: str) -> Optional[Rule]:
        """查找匹配命令的规则"""
        for rule in self.rules:
            if rule.matches(command):
                return rule
        return None
    
    def get_all_rules(self) -> List[Rule]:
        """获取所有规则"""
        return self.rules.copy()
    
    def export_to_bash_script(self, file_path: Union[str, Path]) -> bool:
        """将规则导出为bash脚本"""
        try:
            # 基础脚本模板
            script_template = """#!/bin/bash
LOG_DIRECTORY="{LOG_DIRECTORY}"
LOG_FILENAME="{LOG_FILENAME}"
LOG_FILE="$LOG_DIRECTORY/$LOG_FILENAME"

mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"
chmod 666 "$LOG_FILE" 2>/dev/null

# 非交互式命令处理
if [ -n "$SSH_ORIGINAL_COMMAND" ]; then
  CMD="$SSH_ORIGINAL_COMMAND"
  echo "$(date "+%Y-%m-%d %H:%M:%S") [CMD] $USER: $CMD" >> "$LOG_FILE"

{RULE_BLOCKS}

  # 默认正常执行
  OUTPUT=$(eval "$CMD" 2>&1)
  echo "$OUTPUT"
  exit 0
fi

# 交互式会话处理
echo "$(date "+%Y-%m-%d %H:%M:%S") [SSH] Interactive session started by $USER (PID=$$)" >> "$LOG_FILE"

if command -v script &>/dev/null; then
  script -q --timing="$LOG_FILE.time" -a "$LOG_FILE" -c "/bin/bash"
else
  export HISTFILE="/tmp/.hist.$$"
  export HISTTIMEFORMAT="%F %T "
  export PROMPT_COMMAND='history -a; history 1 >> '"$LOG_FILE"
  trap 'history -a; history 1 >> "$LOG_FILE"' DEBUG
  exec /bin/bash --noprofile --norc
fi
"""
            
            # 构建规则块
            rule_blocks = []
            for rule in self.rules:
                if not rule.enabled:
                    continue
                    
                block = f"  # {rule.name}: {rule.description}\n"
                block += f"  if echo \"$CMD\" | grep -Eq '{rule.pattern}'; then\n"
                
                if rule.action == 'replace':
                    # 输出替换
                    output_lines = rule.output.split('\n')
                    for line in output_lines:
                        block += f"    echo \"{line}\"\n"
                
                elif rule.action == 'script':
                    # 执行脚本
                    script_lines = rule.script.split('\n')
                    for line in script_lines:
                        block += f"    {line}\n"
                
                elif rule.action == 'filter':
                    # 过滤输出
                    block += f"    OUTPUT=$(eval \"$CMD\" 2>&1)\n"
                    if rule.condition:
                        block += f"    if echo \"$OUTPUT\" | {rule.condition}; then\n"
                        block += f"      echo \"$OUTPUT\" | {rule.filter}\n"
                        block += f"    else\n"
                        block += f"      echo \"$OUTPUT\"\n"
                        block += f"    fi\n"
                    else:
                        block += f"    echo \"$OUTPUT\" | {rule.filter}\n"
                
                elif rule.action == 'empty':
                    # 返回空
                    pass
                
                block += "    exit 0\n"
                block += "  fi\n"
                rule_blocks.append(block)
            
            # 替换模板中的参数
            script_content = script_template.replace("{RULE_BLOCKS}", "\n".join(rule_blocks))
            script_content = script_content.replace("{LOG_DIRECTORY}", self.config.log_directory)
            script_content = script_content.replace("{LOG_FILENAME}", self.config.log_filename)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # 设置执行权限
            os.chmod(file_path, 0o755)
            
            return True
        except Exception as e:
            print(f"导出脚本失败: {str(e)}")
            return False
