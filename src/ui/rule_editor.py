from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QPushButton, QTabWidget, QLabel, QGroupBox,
    QMessageBox, QListWidget, QListWidgetItem, QMenu, QToolButton,
    QGridLayout, QSplitter
)
from PySide6.QtGui import QAction

from .visual_rule_editor import VisualRuleEditorDialog

from ..core.rule_manager import Rule, RuleManager
from ..core.mock_engine import MockEngine


class RuleEditorWidget(QWidget):
    """规则编辑器组件"""
    
    # 自定义信号
    rule_saved = Signal()
    
    def __init__(self, rule_manager: RuleManager, mock_engine: MockEngine):
        super().__init__()
        
        self.rule_manager = rule_manager
        self.mock_engine = mock_engine
        self.current_rule_id = None
        
        # 设置UI
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # 规则名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("输入规则名称...")
        form_layout.addRow("规则名称:", self.name_edit)
        
        # 规则描述
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("输入规则描述...")
        form_layout.addRow("规则描述:", self.desc_edit)
        
        # 匹配模式 布局
        pattern_layout = QHBoxLayout()
        
        # 匹配模式输入框
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("输入正则表达式模式...") 
        pattern_layout.addWidget(self.pattern_edit)
        
        # 可视化编辑按钮
        visual_edit_button = QPushButton("可视化编辑")
        visual_edit_button.clicked.connect(self._open_visual_editor)
        pattern_layout.addWidget(visual_edit_button)
        
        # 匹配模式帮助按钮
        pattern_help_button = QToolButton()
        pattern_help_button.setText("帮助")
        pattern_help_button.setPopupMode(QToolButton.InstantPopup)
        pattern_menu = QMenu()
        
        # 常用模式预设
        pattern_presets = [
            ("精确匹配命令", "^command$", "仅匹配精确的命令"),
            ("前缀匹配", "^prefix", "匹配以指定前缀开头的命令"),
            ("后缀匹配", "suffix$", "匹配以指定后缀结尾的命令"),
            ("包含匹配", "pattern", "匹配包含指定内容的命令"),
            ("多选一匹配", "(opt1|opt2|opt3)", "匹配多个选项中的任意一个"),
            ("文件路径匹配", "/path/to/file", "匹配特定的文件路径"),
            ("任意匹配", ".*", "匹配任何内容")
        ]
        
        for name, pattern, tooltip in pattern_presets:
            preset_action = QAction(name, pattern_menu)
            preset_action.setToolTip(tooltip)
            preset_action.setData(pattern)
            preset_action.triggered.connect(lambda checked=False, p=pattern: self._insert_pattern(p))
            pattern_menu.addAction(preset_action)
        
        # 常用命令预设
        pattern_menu.addSeparator()
        pattern_menu.addAction("常用命令预设").setEnabled(False)
        
        common_commands = [
            ("cat读取文件", "cat\\s+/etc/[^\\s]+"),
            ("ls列出文件", "ls\\s+-\\w+\\s+/\\S+"),
            ("执行脚本", "(sh|bash)\\s+\\S+"),
            ("系统服务命令", "systemctl\\s+\\w+\\s+\\S+"),
            ("查找文件", "find\\s+/\\S+\\s+-name\\s+\\S+"),
            ("查看进程", "ps\\s+(aux|ef)")
        ]
        
        for name, pattern in common_commands:
            cmd_action = QAction(name, pattern_menu)
            cmd_action.setData(pattern)
            cmd_action.triggered.connect(lambda checked=False, p=pattern: self._insert_pattern(p))
            pattern_menu.addAction(cmd_action)
        
        pattern_help_button.setMenu(pattern_menu)
        pattern_layout.addWidget(pattern_help_button)
        
        form_layout.addRow("匹配模式:", pattern_layout)
        
        # 动作类型
        self.action_combo = QComboBox()
        self.action_combo.addItems(["替换输出", "自定义脚本", "过滤输出", "返回空"])
        self.action_combo.currentIndexChanged.connect(self._handle_action_changed)
        form_layout.addRow("动作类型:", self.action_combo)
        
        # 启用状态
        self.enabled_check = QCheckBox("启用此规则")
        self.enabled_check.setChecked(True)
        form_layout.addRow("", self.enabled_check)
        
        main_layout.addLayout(form_layout)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 动作详情选项卡
        self.action_tab = QWidget()
        self.tab_widget.addTab(self.action_tab, "动作详情")
        
        # 测试选项卡
        self.test_tab = QWidget()
        self.tab_widget.addTab(self.test_tab, "规则测试")
        
        self._setup_action_tab()
        self._setup_test_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 保存按钮
        self.save_button = QPushButton("保存规则")
        self.save_button.clicked.connect(self._handle_save_button_clicked)
        button_layout.addWidget(self.save_button)
        
        # 取消按钮
        self.cancel_button = QPushButton("清空表单")
        self.cancel_button.clicked.connect(self.clear)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.setAlignment(Qt.AlignRight)
        
        main_layout.addLayout(button_layout)
    
    def _setup_action_tab(self):
        """设置动作详情选项卡"""
        layout = QVBoxLayout(self.action_tab)
        
        # 创建堆叠小部件
        self.action_group = QGroupBox("动作参数")
        layout.addWidget(self.action_group)
        
        # 创建包含所有布局的容器小部件
        self.replace_container = QWidget()
        self.script_container = QWidget()
        self.filter_container = QWidget()
        self.empty_container = QWidget()
        
        # 替换输出设置
        self.replace_layout = QVBoxLayout(self.replace_container)
        
        # 输出内容编辑器
        self.output_edit = QTextEdit()
        self.output_edit.setPlaceholderText("输入要返回的内容...可以包含多行文本")
        self.output_edit.setMinimumHeight(200)  # 增加高度，更易于编辑
        
        output_label = QLabel("替换输出内容:")
        output_help = QLabel("（每行将作为单独的输出行，可使用空行创建空行输出）")
        output_help.setStyleSheet("color: #666;")
        
        self.replace_layout.addWidget(output_label)
        self.replace_layout.addWidget(output_help)
        self.replace_layout.addWidget(self.output_edit)
        
        # 自定义脚本设置
        self.script_layout = QVBoxLayout(self.script_container)
        
        script_label = QLabel("脚本内容:")
        script_help = QLabel("（可使用$CMD变量引用原始命令，用于复杂的处理逻辑）")
        script_help.setStyleSheet("color: #666;")
        
        self.script_edit = QTextEdit()
        self.script_edit.setPlaceholderText("输入Bash脚本代码...\n可使用$CMD变量引用原始命令\n脚本应该生成最终的输出结果")
        self.script_edit.setMinimumHeight(200)  # 增加高度，更易于编辑
        
        self.script_layout.addWidget(script_label)
        self.script_layout.addWidget(script_help)
        self.script_layout.addWidget(self.script_edit)
        
        # 过滤输出设置
        self.filter_layout = QVBoxLayout(self.filter_container)
        
        filter_label = QLabel("过滤命令:")
        filter_help = QLabel("（指定如何处理原始命令输出，如: sed 's/foo/bar/g'）")
        filter_help.setStyleSheet("color: #666;")
        
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("输入过滤命令，如: sed 's/foo/bar/g'")
        
        self.filter_layout.addWidget(filter_label)
        self.filter_layout.addWidget(filter_help)
        self.filter_layout.addWidget(self.filter_edit)
        
        condition_label = QLabel("应用条件(可选):")
        condition_help = QLabel("（仅当输出满足此条件时才应用过滤，如: grep -q 'pattern'）")
        condition_help.setStyleSheet("color: #666;")
        
        self.condition_edit = QLineEdit()
        self.condition_edit.setPlaceholderText("输入条件，如: grep -q 'pattern'，留空则始终应用过滤")
        
        self.filter_layout.addWidget(condition_label)
        self.filter_layout.addWidget(condition_help)
        self.filter_layout.addWidget(self.condition_edit)
        
        # 空输出设置
        self.empty_layout = QVBoxLayout(self.empty_container)
        empty_label = QLabel("此操作将直接返回空输出，无需额外参数。")
        empty_help = QLabel("（对于需要隐藏或屏蔽的命令，如读取敏感文件、反弹shell等）")
        empty_help.setStyleSheet("color: #666;")
        self.empty_layout.addWidget(empty_label)
        self.empty_layout.addWidget(empty_help)
        
        # 创建一个初始布局
        self.action_layout = QVBoxLayout(self.action_group)
        
        # 添加所有容器到布局，默认只显示替换输出容器
        self.action_layout.addWidget(self.replace_container)
        self.action_layout.addWidget(self.script_container)
        self.action_layout.addWidget(self.filter_container)
        self.action_layout.addWidget(self.empty_container)
        
        # 隐藏除替换输出外的其他容器
        self.replace_container.setVisible(True)
        self.script_container.setVisible(False)
        self.filter_container.setVisible(False)
        self.empty_container.setVisible(False)
    
    def _setup_test_tab(self):
        """设置测试选项卡"""
        layout = QVBoxLayout(self.test_tab)
        
        # 测试命令输入
        self.test_command_edit = QLineEdit()
        self.test_command_edit.setPlaceholderText("输入要测试的命令...")
        layout.addWidget(QLabel("测试命令:"))
        layout.addWidget(self.test_command_edit)
        
        # 测试按钮
        self.test_button = QPushButton("运行测试")
        self.test_button.clicked.connect(self._handle_test_button_clicked)
        layout.addWidget(self.test_button)
        
        # 结果输出
        layout.addWidget(QLabel("测试结果:"))
        self.test_result_edit = QTextEdit()
        self.test_result_edit.setReadOnly(True)
        layout.addWidget(self.test_result_edit)
    
    def load_rule(self, rule: Rule):
        """加载规则到编辑器"""
        if not rule:
            return
        
        self.current_rule_id = rule.id
        
        # 基本信息
        self.name_edit.setText(rule.name)
        self.desc_edit.setText(rule.description)
        self.pattern_edit.setText(rule.pattern)
        self.enabled_check.setChecked(rule.enabled)
        
        # 动作类型
        action_index_map = {
            'replace': 0,
            'script': 1,
            'filter': 2,
            'empty': 3
        }
        action_index = action_index_map.get(rule.action, 0)
        self.action_combo.setCurrentIndex(action_index)
        
        # 动作参数
        if rule.action == 'replace':
            self.output_edit.setText(rule.output)
        elif rule.action == 'script':
            self.script_edit.setText(rule.script)
        elif rule.action == 'filter':
            self.filter_edit.setText(rule.filter)
            self.condition_edit.setText(rule.condition)
    
    def clear(self):
        """清空编辑器"""
        self.current_rule_id = None
        
        # 清空基本信息
        self.name_edit.clear()
        self.desc_edit.clear()
        self.pattern_edit.clear()
        self.enabled_check.setChecked(True)
        
        # 重置动作类型
        self.action_combo.setCurrentIndex(0)
        
        # 清空动作参数
        self.output_edit.clear()
        self.script_edit.clear()
        self.filter_edit.clear()
        self.condition_edit.clear()
        
        # 清空测试
        self.test_command_edit.clear()
        self.test_result_edit.clear()
    
    def _get_current_action_type(self):
        """获取当前选择的动作类型"""
        action_map = {
            0: 'replace',
            1: 'script',
            2: 'filter',
            3: 'empty'
        }
        return action_map.get(self.action_combo.currentIndex(), 'replace')
    
    def _insert_pattern(self, pattern):
        """将模式插入到匹配模式输入框"""
        current_text = self.pattern_edit.text()
        # 如果当前为空或是默认的通配符模式，直接替换
        if not current_text or current_text == ".*":
            self.pattern_edit.setText(pattern)
        # 否则考虑组合成复合表达式
        else:
            # 如果用户已经在创建复合表达式，考虑如何最好地组合
            msg_box = QMessageBox()
            msg_box.setWindowTitle("选择组合方式")
            msg_box.setText("您已经有一个模式，请选择如何组合新模式:")
            
            replace_button = msg_box.addButton("替换现有模式", QMessageBox.AcceptRole)
            or_button = msg_box.addButton("添加为或(|)关系", QMessageBox.AcceptRole)
            and_button = msg_box.addButton("添加为且(行首^)关系", QMessageBox.AcceptRole)
            cancel_button = msg_box.addButton(QMessageBox.Cancel)
            
            msg_box.exec()
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == replace_button:
                self.pattern_edit.setText(pattern)
            elif clicked_button == or_button:
                # 使用|组合两个模式（或关系）
                self.pattern_edit.setText(f"({current_text}|{pattern})")
            elif clicked_button == and_button:
                # 使用前缀^来组合（逻辑上类似且关系）
                self.pattern_edit.setText(f"^{current_text}.*{pattern}")
                
    def _open_visual_editor(self):
        """打开可视化规则编辑器"""
        # 创建可视化编辑器对话框
        dialog = VisualRuleEditorDialog(self, self.pattern_edit.text())
        
        # 连接信号
        dialog.pattern_generated.connect(self._set_pattern_from_visual_editor)
        
        # 显示对话框
        dialog.exec()
    
    def _set_pattern_from_visual_editor(self, pattern):
        """设置可视化编辑器生成的模式"""
        if pattern:
            self.pattern_edit.setText(pattern)
    
    def _handle_action_changed(self, index):
        """处理动作类型变更事件"""
        # 隐藏所有容器
        self.replace_container.setVisible(False)
        self.script_container.setVisible(False)
        self.filter_container.setVisible(False)
        self.empty_container.setVisible(False)
        
        # 显示选定的容器
        if index == 0:  # 替换输出
            self.replace_container.setVisible(True)
        elif index == 1:  # 自定义脚本
            self.script_container.setVisible(True)
        elif index == 2:  # 过滤输出
            self.filter_container.setVisible(True)
        elif index == 3:  # 返回空
            self.empty_container.setVisible(True)
    
    def _handle_save_button_clicked(self):
        """处理保存按钮点击事件"""
        # 验证必填字段
        if not self.name_edit.text():
            QMessageBox.warning(self, "验证失败", "规则名称不能为空")
            return
        
        if not self.pattern_edit.text():
            QMessageBox.warning(self, "验证失败", "匹配模式不能为空")
            return
        
        # 获取动作类型相关参数
        action_type = self._get_current_action_type()
        kwargs = {}
        
        if action_type == 'replace':
            if not self.output_edit.toPlainText():
                QMessageBox.warning(self, "验证失败", "替换输出内容不能为空")
                return
            kwargs['output'] = self.output_edit.toPlainText()
        
        elif action_type == 'script':
            if not self.script_edit.toPlainText():
                QMessageBox.warning(self, "验证失败", "脚本内容不能为空")
                return
            kwargs['script'] = self.script_edit.toPlainText()
        
        elif action_type == 'filter':
            if not self.filter_edit.text():
                QMessageBox.warning(self, "验证失败", "过滤命令不能为空")
                return
            kwargs['filter'] = self.filter_edit.text()
            kwargs['condition'] = self.condition_edit.text()
        
        # 创建规则对象
        rule = Rule(
            self.current_rule_id or 0,
            self.name_edit.text(),
            self.desc_edit.text(),
            self.pattern_edit.text(),
            action_type,
            self.enabled_check.isChecked(),
            **kwargs
        )
        
        # 保存规则
        if self.current_rule_id:
            success = self.rule_manager.update_rule(rule)
        else:
            rule_id = self.rule_manager.add_rule(rule)
            self.current_rule_id = rule_id
            success = rule_id > 0
        
        if success:
            # 发送规则保存信号
            self.rule_saved.emit()
            
            # 显示成功消息
            QMessageBox.information(self, "保存成功", "规则已成功保存")
        else:
            QMessageBox.warning(self, "保存失败", "无法保存规则")
    
    def _handle_test_button_clicked(self):
        """处理测试按钮点击事件"""
        # 获取测试命令
        command = self.test_command_edit.text()
        if not command:
            QMessageBox.warning(self, "测试失败", "请输入测试命令")
            return
            
        # 先保存当前规则的所有更改，以确保测试使用最新的设置
        action_type = self._get_current_action_type()
        if action_type == 'replace' and not self.output_edit.toPlainText().strip():
            QMessageBox.warning(self, "测试失败", "请先输入替换输出内容")
            return
        elif action_type == 'script' and not self.script_edit.toPlainText().strip():
            QMessageBox.warning(self, "测试失败", "请先输入脚本内容")
            return
        elif action_type == 'filter' and not self.filter_edit.text().strip():
            QMessageBox.warning(self, "测试失败", "请先输入过滤命令")
            return
        
        try:
            # 创建临时规则用于测试
            action_type = self._get_current_action_type()
            kwargs = {}
            
            if action_type == 'replace':
                kwargs['output'] = self.output_edit.toPlainText()
            elif action_type == 'script':
                kwargs['script'] = self.script_edit.toPlainText()
            elif action_type == 'filter':
                kwargs['filter'] = self.filter_edit.text()
                kwargs['condition'] = self.condition_edit.text()
            
            temp_rule = Rule(
                0,
                self.name_edit.text() or "测试规则",
                self.desc_edit.text() or "测试描述",
                self.pattern_edit.text() or ".*",
                action_type,
                True,
                **kwargs
            )
            
            # 使用模拟引擎测试规则
            result = self.mock_engine.preview_rule(command, temp_rule)
            
            # 显示结果
            self.test_result_edit.setText(result)
        except Exception as e:
            # 显示错误信息
            self.test_result_edit.setText(f"测试失败: {str(e)}")
