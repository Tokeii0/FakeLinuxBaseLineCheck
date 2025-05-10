from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QCheckBox, QGroupBox, QRadioButton,
    QMessageBox, QWidget, QFormLayout, QListWidget,
    QListWidgetItem, QTabWidget, QToolButton, QMenu
)
from PySide6.QtGui import QAction


class VisualRuleEditorDialog(QDialog):
    """可视化规则编辑器对话框"""
    
    # 自定义信号
    pattern_generated = Signal(str)
    
    def __init__(self, parent=None, current_pattern=""):
        super().__init__(parent)
        
        self.setWindowTitle("可视化规则编辑器")
        self.setMinimumSize(700, 500)
        
        # 存储原始模式
        self.current_pattern = current_pattern
        
        # 初始化UI
        self._setup_ui()
        
        # 如果有现有模式，尝试解析它
        if current_pattern:
            self._parse_existing_pattern(current_pattern)
    
    def _setup_ui(self):
        """设置UI组件"""
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 基本匹配选项卡
        basic_tab = QWidget()
        tab_widget.addTab(basic_tab, "基本匹配")
        self._setup_basic_tab(basic_tab)
        
        # 命令选项卡
        command_tab = QWidget()
        tab_widget.addTab(command_tab, "命令匹配")
        self._setup_command_tab(command_tab)
        
        # 文件选项卡
        file_tab = QWidget()
        tab_widget.addTab(file_tab, "文件匹配")
        self._setup_file_tab(file_tab)
        
        # 高级选项卡
        advanced_tab = QWidget()
        tab_widget.addTab(advanced_tab, "高级组合")
        self._setup_advanced_tab(advanced_tab)
        
        # 预览区域
        preview_group = QGroupBox("规则预览")
        preview_layout = QVBoxLayout(preview_group)
        
        # 预览标签
        preview_label = QLabel("生成的规则模式:")
        preview_layout.addWidget(preview_label)
        
        # 预览文本框
        self.preview_edit = QLineEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setPlaceholderText("在选项卡中设置参数后生成规则模式")
        preview_layout.addWidget(self.preview_edit)
        
        main_layout.addWidget(preview_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 生成按钮
        generate_button = QPushButton("生成并应用")
        generate_button.clicked.connect(self._handle_generate)
        button_layout.addWidget(generate_button)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        button_layout.setAlignment(Qt.AlignRight)
        main_layout.addLayout(button_layout)
    
    def _setup_basic_tab(self, tab):
        """设置基本匹配选项卡"""
        layout = QVBoxLayout(tab)
        
        # 匹配类型
        type_group = QGroupBox("匹配类型")
        type_layout = QVBoxLayout(type_group)
        
        self.exact_radio = QRadioButton("精确匹配")
        self.exact_radio.setChecked(True)
        self.exact_radio.toggled.connect(self._update_preview)
        type_layout.addWidget(self.exact_radio)
        
        self.contains_radio = QRadioButton("包含匹配")
        self.contains_radio.toggled.connect(self._update_preview)
        type_layout.addWidget(self.contains_radio)
        
        self.prefix_radio = QRadioButton("前缀匹配")
        self.prefix_radio.toggled.connect(self._update_preview)
        type_layout.addWidget(self.prefix_radio)
        
        self.suffix_radio = QRadioButton("后缀匹配")
        self.suffix_radio.toggled.connect(self._update_preview)
        type_layout.addWidget(self.suffix_radio)
        
        self.regex_radio = QRadioButton("正则表达式匹配")
        self.regex_radio.toggled.connect(self._update_preview)
        type_layout.addWidget(self.regex_radio)
        
        layout.addWidget(type_group)
        
        # 匹配内容
        content_group = QGroupBox("匹配内容")
        content_layout = QFormLayout(content_group)
        
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText("输入要匹配的内容...")
        self.content_edit.textChanged.connect(self._update_preview)
        content_layout.addRow("内容:", self.content_edit)
        
        self.case_check = QCheckBox("区分大小写")
        self.case_check.toggled.connect(self._update_preview)
        content_layout.addRow("", self.case_check)
        
        layout.addWidget(content_group)
        
        # 通用选项
        options_group = QGroupBox("选项")
        options_layout = QVBoxLayout(options_group)
        
        self.entire_line_check = QCheckBox("匹配整行")
        self.entire_line_check.toggled.connect(self._update_preview)
        options_layout.addWidget(self.entire_line_check)
        
        layout.addWidget(options_group)
        
        # 添加弹性空间
        layout.addStretch(1)
    
    def _setup_command_tab(self, tab):
        """设置命令匹配选项卡"""
        layout = QVBoxLayout(tab)
        
        # 命令类型
        cmd_group = QGroupBox("命令类型")
        cmd_layout = QVBoxLayout(cmd_group)
        
        self.cmd_types = [
            ("任意命令", ".*"),
            ("文件操作", "(cat|ls|cp|mv|rm)"),
            ("进程管理", "(ps|kill|pkill)"),
            ("网络命令", "(wget|curl|netstat|ifconfig|ping)"),
            ("系统管理", "(systemctl|service|chkconfig)"),
            ("用户管理", "(useradd|userdel|usermod|passwd)"),
            ("脚本执行", "(bash|sh|python|perl)")
        ]
        
        self.cmd_radios = []
        for name, pattern in self.cmd_types:
            radio = QRadioButton(name)
            radio.setProperty("pattern", pattern)
            radio.toggled.connect(self._update_preview)
            cmd_layout.addWidget(radio)
            self.cmd_radios.append(radio)
        
        # 默认选中第一个
        self.cmd_radios[0].setChecked(True)
        
        layout.addWidget(cmd_group)
        
        # 命令参数
        arg_group = QGroupBox("命令参数")
        arg_layout = QFormLayout(arg_group)
        
        self.arg_edit = QLineEdit()
        self.arg_edit.setPlaceholderText("输入要匹配的命令参数...")
        self.arg_edit.textChanged.connect(self._update_preview)
        arg_layout.addRow("参数:", self.arg_edit)
        
        self.arg_exact_check = QCheckBox("精确匹配参数")
        self.arg_exact_check.toggled.connect(self._update_preview)
        arg_layout.addRow("", self.arg_exact_check)
        
        layout.addWidget(arg_group)
        
        # 添加弹性空间
        layout.addStretch(1)
    
    def _setup_file_tab(self, tab):
        """设置文件匹配选项卡"""
        layout = QVBoxLayout(tab)
        
        # 文件路径
        path_group = QGroupBox("文件路径")
        path_layout = QFormLayout(path_group)
        
        self.dir_paths = QComboBox()
        self.dir_paths.addItems([
            "/etc", "/var", "/usr", "/bin", "/sbin", "/home", "/tmp", "/dev"
        ])
        self.dir_paths.setEditable(True)
        self.dir_paths.currentTextChanged.connect(self._update_preview)
        path_layout.addRow("目录:", self.dir_paths)
        
        self.file_filter = QLineEdit()
        self.file_filter.setPlaceholderText("输入文件名或通配符...")
        self.file_filter.textChanged.connect(self._update_preview)
        path_layout.addRow("文件:", self.file_filter)
        
        layout.addWidget(path_group)
        
        # 文件操作
        op_group = QGroupBox("文件操作")
        op_layout = QVBoxLayout(op_group)
        
        self.file_ops = [
            ("读取文件", "cat"),
            ("列出文件", "ls"),
            ("复制文件", "cp"),
            ("移动文件", "mv"),
            ("删除文件", "rm"),
            ("修改权限", "chmod"),
            ("修改所有者", "chown"),
            ("编辑文件", "(vim|nano|vi)")
        ]
        
        self.op_checkboxes = []
        for name, op in self.file_ops:
            check = QCheckBox(name)
            check.setProperty("op", op)
            check.toggled.connect(self._update_preview)
            op_layout.addWidget(check)
            self.op_checkboxes.append(check)
        
        # 默认选中第一个
        self.op_checkboxes[0].setChecked(True)
        
        layout.addWidget(op_group)
        
        # 添加弹性空间
        layout.addStretch(1)
    
    def _setup_advanced_tab(self, tab):
        """设置高级组合选项卡"""
        layout = QVBoxLayout(tab)
        
        # 规则列表
        rules_group = QGroupBox("规则列表")
        rules_layout = QVBoxLayout(rules_group)
        
        self.rules_list = QListWidget()
        rules_layout.addWidget(self.rules_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("添加规则")
        add_button.clicked.connect(self._add_rule)
        button_layout.addWidget(add_button)
        
        delete_button = QPushButton("删除规则")
        delete_button.clicked.connect(self._delete_rule)
        button_layout.addWidget(delete_button)
        
        rules_layout.addLayout(button_layout)
        
        layout.addWidget(rules_group)
        
        # 组合方式
        combine_group = QGroupBox("组合方式")
        combine_layout = QVBoxLayout(combine_group)
        
        self.or_radio = QRadioButton("或关系 (匹配任意一个)")
        self.or_radio.setChecked(True)
        self.or_radio.toggled.connect(self._update_preview)
        combine_layout.addWidget(self.or_radio)
        
        self.and_radio = QRadioButton("且关系 (必须全部匹配)")
        self.and_radio.toggled.connect(self._update_preview)
        combine_layout.addWidget(self.and_radio)
        
        layout.addWidget(combine_group)
        
        # 原始正则表达式
        regex_group = QGroupBox("原始正则表达式")
        regex_layout = QVBoxLayout(regex_group)
        
        self.regex_edit = QLineEdit()
        self.regex_edit.setPlaceholderText("输入或修改原始正则表达式...")
        self.regex_edit.textChanged.connect(self._handle_regex_changed)
        regex_layout.addWidget(self.regex_edit)
        
        # 按钮
        regex_button_layout = QHBoxLayout()
        
        apply_button = QPushButton("应用正则表达式")
        apply_button.clicked.connect(lambda: self.preview_edit.setText(self.regex_edit.text()))
        regex_button_layout.addWidget(apply_button)
        
        reset_button = QPushButton("重置")
        reset_button.clicked.connect(self._update_preview)
        regex_button_layout.addWidget(reset_button)
        
        regex_layout.addLayout(regex_button_layout)
        
        layout.addWidget(regex_group)
    
    def _update_preview(self):
        """更新预览"""
        try:
            # 当前如果没有选项卡激活，使用默认值
            pattern = ""
            
            # 得到当前激活的选项卡索引
            current_index = 0
            for widget in self.findChildren(QTabWidget):
                current_index = widget.currentIndex()
                break
                
            # 根据选中的选项卡生成模式
            if current_index == 0:  # 基本匹配
                pattern = self._get_pattern_from_basic_tab()
            elif current_index == 1:  # 命令匹配
                pattern = self._get_pattern_from_command_tab()
            elif current_index == 2:  # 文件匹配
                pattern = self._get_pattern_from_file_tab()
            elif current_index == 3:  # 高级组合
                pattern = self._get_pattern_from_advanced_tab()
            
            # 更新预览
            if hasattr(self, 'preview_edit') and self.preview_edit:
                self.preview_edit.setText(pattern)
        except Exception as e:
            # 错误处理
            print(f"更新预览时出错: {str(e)}")
    
    def _handle_regex_changed(self):
        """处理正则表达式变更"""
        # 不自动更新预览，需要用户点击应用
        pass
    
    def _get_pattern_from_basic_tab(self):
        """从基本选项卡获取模式"""
        try:
            if not hasattr(self, 'content_edit') or not self.content_edit:
                return ""
                
            content = self.content_edit.text()
            if not content:
                return ""
            
            # 处理特殊字符
            content = self._escape_regex_chars(content)
            
            # 根据匹配类型处理
            if hasattr(self, 'exact_radio') and self.exact_radio.isChecked():
                pattern = f"^{content}$"
            elif hasattr(self, 'contains_radio') and self.contains_radio.isChecked():
                pattern = content
            elif hasattr(self, 'prefix_radio') and self.prefix_radio.isChecked():
                pattern = f"^{content}"
            elif hasattr(self, 'suffix_radio') and self.suffix_radio.isChecked():
                pattern = f"{content}$"
            elif hasattr(self, 'regex_radio') and self.regex_radio.isChecked():
                pattern = self.content_edit.text()  # 不转义
            else:
                pattern = content
            
            # 处理大小写
            if hasattr(self, 'case_check') and (not self.case_check.isChecked()) and \
               (not hasattr(self, 'regex_radio') or not self.regex_radio.isChecked()):
                pattern = f"(?i){pattern}"
            
            # 处理整行匹配
            if hasattr(self, 'entire_line_check') and self.entire_line_check.isChecked() and \
               not (hasattr(self, 'exact_radio') and self.exact_radio.isChecked() or \
                    hasattr(self, 'regex_radio') and self.regex_radio.isChecked()):
                pattern = f"^{pattern}$"
            
            return pattern
        except Exception as e:
            print(f"从基本选项卡获取模式时出错: {str(e)}")
            return ""
    
    def _get_pattern_from_command_tab(self):
        """从命令选项卡获取模式"""
        try:
            if not hasattr(self, 'cmd_radios') or not self.cmd_radios:
                return ""
                
            # 获取命令类型
            cmd_pattern = ""
            for radio in self.cmd_radios:
                if radio.isChecked():
                    cmd_pattern = radio.property("pattern")
                    break
            
            # 获取参数
            if hasattr(self, 'arg_edit') and self.arg_edit:
                arg = self.arg_edit.text()
                if arg:
                    arg = self._escape_regex_chars(arg)
                    if hasattr(self, 'arg_exact_check') and self.arg_exact_check.isChecked():
                        arg_pattern = f"\\s+{arg}($|\\s)"
                    else:
                        arg_pattern = f"\\s+.*{arg}"
                    
                    return f"{cmd_pattern}{arg_pattern}"
            
            return cmd_pattern
        except Exception as e:
            print(f"从命令选项卡获取模式时出错: {str(e)}")
            return ""
    
    def _get_pattern_from_file_tab(self):
        """从文件选项卡获取模式"""
        try:
            if not hasattr(self, 'dir_paths') or not self.dir_paths:
                return ""
                
            # 获取目录路径
            dir_path = self.dir_paths.currentText()
            if not dir_path:
                dir_path = "/"
            
            # 获取文件名
            if hasattr(self, 'file_filter') and self.file_filter:
                file_name = self.file_filter.text()
                if file_name:
                    file_pattern = f"{dir_path}/{file_name}"
                else:
                    file_pattern = f"{dir_path}/[^\\s]+"
            else:
                file_pattern = f"{dir_path}/[^\\s]+"
            
            # 获取选中的文件操作
            if hasattr(self, 'op_checkboxes') and self.op_checkboxes:
                ops = []
                for check in self.op_checkboxes:
                    if check.isChecked():
                        ops.append(check.property("op"))
                
                if ops:
                    op_pattern = "|".join(ops)
                    if len(ops) > 1:
                        op_pattern = f"({op_pattern})"
                    
                    return f"{op_pattern}\\s+{file_pattern}"
            
            return file_pattern
        except Exception as e:
            print(f"从文件选项卡获取模式时出错: {str(e)}")
            return ""
    
    def _get_pattern_from_advanced_tab(self):
        """从高级选项卡获取模式"""
        try:
            if not hasattr(self, 'rules_list') or not self.rules_list:
                return ""
                
            # 获取规则列表
            rules = []
            for i in range(self.rules_list.count()):
                item = self.rules_list.item(i)
                if item and item.data(Qt.UserRole):
                    rules.append(item.data(Qt.UserRole))
            
            if not rules:
                if hasattr(self, 'regex_edit') and self.regex_edit:
                    return self.regex_edit.text() or ""
                return ""
            
            # 根据组合方式处理
            if hasattr(self, 'or_radio') and self.or_radio.isChecked():
                # 或关系
                pattern = "|".join(rules)
                if len(rules) > 1:
                    pattern = f"({pattern})"
            else:
                # 且关系
                pattern = "".join([f"(?=.*{rule})" for rule in rules])
                pattern = f"^{pattern}.*$"
            
            return pattern
        except Exception as e:
            print(f"从高级选项卡获取模式时出错: {str(e)}")
            return ""
    
    def _escape_regex_chars(self, text):
        """转义正则表达式特殊字符"""
        special_chars = r".[{()*+?|^$\\"
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
        return text
    
    def _add_rule(self):
        """添加规则"""
        pattern = self.preview_edit.text()
        if not pattern:
            QMessageBox.warning(self, "添加失败", "请先在其他选项卡创建规则")
            return
        
        # 添加规则到列表
        item = QListWidgetItem(f"规则: {pattern}")
        item.setData(Qt.UserRole, pattern)
        self.rules_list.addItem(item)
        
        # 更新预览
        self._update_preview()
    
    def _delete_rule(self):
        """删除规则"""
        current_item = self.rules_list.currentItem()
        if current_item:
            self.rules_list.takeItem(self.rules_list.row(current_item))
            
            # 更新预览
            self._update_preview()
    
    def _handle_generate(self):
        """处理生成按钮点击事件"""
        pattern = self.preview_edit.text()
        if not pattern:
            QMessageBox.warning(self, "生成失败", "请先创建规则")
            return
        
        # 发送信号
        self.pattern_generated.emit(pattern)
        
        # 接受对话框
        self.accept()
    
    def _parse_existing_pattern(self, pattern):
        """解析现有模式"""
        # 设置到高级选项卡的正则表达式编辑框
        self.regex_edit.setText(pattern)
        
        # 尝试简单解析以设置适当的控件状态
        # 这里只做简单的解析，完整解析正则表达式非常复杂
        
        if pattern.startswith("^") and pattern.endswith("$"):
            # 完全匹配
            self.exact_radio.setChecked(True)
            content = pattern[1:-1]
            self.content_edit.setText(self._unescape_regex_chars(content))
        
        elif pattern.startswith("^"):
            # 前缀匹配
            self.prefix_radio.setChecked(True)
            content = pattern[1:]
            self.content_edit.setText(self._unescape_regex_chars(content))
        
        elif pattern.endswith("$"):
            # 后缀匹配
            self.suffix_radio.setChecked(True)
            content = pattern[:-1]
            self.content_edit.setText(self._unescape_regex_chars(content))
        
        elif "(?i)" in pattern:
            # 不区分大小写
            self.case_check.setChecked(False)
            self.contains_radio.setChecked(True)
            content = pattern.replace("(?i)", "")
            self.content_edit.setText(self._unescape_regex_chars(content))
        
        elif pattern.startswith("(") and "|" in pattern:
            # 或关系
            self.or_radio.setChecked(True)
            
            # 添加到规则列表
            parts = pattern[1:-1].split("|")
            for part in parts:
                item = QListWidgetItem(f"规则: {part}")
                item.setData(Qt.UserRole, part)
                self.rules_list.addItem(item)
        
        else:
            # 假设是简单的包含匹配
            self.contains_radio.setChecked(True)
            self.content_edit.setText(self._unescape_regex_chars(pattern))
    
    def _unescape_regex_chars(self, text):
        """反转义正则表达式特殊字符"""
        # 简化版反转义，仅处理基本情况
        special_chars = r".[{()*+?|^$\\"
        for char in special_chars:
            text = text.replace(f"\\{char}", char)
        return text
