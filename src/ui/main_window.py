import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, 
    QToolBar, QStatusBar, QMessageBox, QFileDialog, 
    QFormLayout, QLineEdit, QPushButton, QLabel, QGroupBox
)

from ..core.rule_manager import RuleManager
from ..core.mock_engine import MockEngine
from .rule_editor import RuleEditorWidget
from .rule_list import RuleListWidget


class MainWindow(QMainWindow):
    """应用程序主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("Linux命令伪装配置工具")
        self.setMinimumSize(900, 600)
        
        # 初始化规则管理器
        self.rule_manager = RuleManager()
        self.mock_engine = MockEngine(self.rule_manager)
        
        # 加载默认规则
        self._load_default_rules()
        
        # 设置UI组件
        self._setup_ui()
        
        # 加载样式表
        self._load_stylesheet()
    
    def _setup_ui(self):
        """设置UI组件"""
        # 创建中央部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建布局
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建规则列表页面
        self.rule_list_widget = RuleListWidget(self.rule_manager)
        self.tab_widget.addTab(self.rule_list_widget, "规则列表")
        
        # 创建规则编辑页面
        self.rule_editor_widget = RuleEditorWidget(self.rule_manager, self.mock_engine)
        self.tab_widget.addTab(self.rule_editor_widget, "规则编辑")
        
        # 创建设置页面
        self.settings_widget = self._create_settings_widget()
        self.tab_widget.addTab(self.settings_widget, "设置")
        
        # 连接信号
        self.rule_list_widget.rule_selected.connect(self._handle_rule_selected)
        self.rule_list_widget.rule_added.connect(self._handle_rule_added)
        self.rule_editor_widget.rule_saved.connect(self._handle_rule_saved)
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建工具栏
        self._create_tool_bar()
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        # 新建规则
        new_action = QAction("新建规则", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._create_new_rule)
        file_menu.addAction(new_action)
        
        # 打开配置
        open_action = QAction("打开配置", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_config)
        file_menu.addAction(open_action)
        
        # 保存配置
        save_action = QAction("保存配置", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_config)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 导出Bash脚本
        export_action = QAction("导出Bash脚本", self)
        export_action.triggered.connect(self._export_script)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = self.menuBar().addMenu("编辑")
        
        # 删除规则
        delete_action = QAction("删除规则", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self._delete_rule)
        edit_menu.addAction(delete_action)
        
        # 启用/禁用规则
        toggle_action = QAction("启用/禁用规则", self)
        toggle_action.triggered.connect(self._toggle_rule)
        edit_menu.addAction(toggle_action)
        
        # 复制规则
        duplicate_action = QAction("复制规则", self)
        duplicate_action.setShortcut("Ctrl+D")
        duplicate_action.triggered.connect(self._duplicate_rule)
        edit_menu.addAction(duplicate_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # 新建规则
        new_action = QAction("新建", self)
        new_action.triggered.connect(self._create_new_rule)
        toolbar.addAction(new_action)
        
        # 保存配置
        save_action = QAction("保存", self)
        save_action.triggered.connect(self._save_config)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 导出脚本
        export_action = QAction("导出", self)
        export_action.triggered.connect(self._export_script)
        toolbar.addAction(export_action)
    
    def _load_stylesheet(self):
        """加载QSS样式表"""
        try:
            # 获取样式表文件路径
            base_dir = Path(__file__).parent.parent.parent
            style_path = base_dir / "src" / "resources" / "styles" / "main.qss"
            
            # 读取样式表
            with open(style_path, "r", encoding="utf-8") as f:
                stylesheet = f.read()
                
            # 应用样式表
            self.setStyleSheet(stylesheet)
        except Exception as e:
            print(f"加载样式表失败: {str(e)}")
    
    def _create_settings_widget(self):
        """创建设置页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 日志设置组
        log_group = QGroupBox("日志设置")
        log_layout = QFormLayout(log_group)
        
        # 日志目录输入框
        self.log_dir_edit = QLineEdit(self.rule_manager.config.log_directory)
        log_dir_label = QLabel("日志输出目录:")
        log_layout.addRow(log_dir_label, self.log_dir_edit)
        
        # 浏览按钮
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self._browse_log_directory)
        log_layout.addRow("", browse_button)
        
        # 日志文件名输入框
        self.log_filename_edit = QLineEdit(self.rule_manager.config.log_filename)
        log_filename_label = QLabel("日志文件名:")
        log_layout.addRow(log_filename_label, self.log_filename_edit)
        
        layout.addWidget(log_group)
        
        # 保存设置按钮
        save_settings_button = QPushButton("保存设置")
        save_settings_button.clicked.connect(self._save_settings)
        layout.addWidget(save_settings_button, alignment=Qt.AlignRight)
        
        # 添加垂直弹性空间
        layout.addStretch(1)
        
        return widget
        
    def _browse_log_directory(self):
        """浏览选择日志目录"""
        directory = QFileDialog.getExistingDirectory(
            self, "选择日志输出目录", self.log_dir_edit.text()
        )
        
        if directory:
            self.log_dir_edit.setText(directory)
    
    def _save_settings(self):
        """保存设置"""
        # 更新配置
        self.rule_manager.config.log_directory = self.log_dir_edit.text()
        self.rule_manager.config.log_filename = self.log_filename_edit.text()
        
        # 显示成功消息
        QMessageBox.information(self, "设置已保存", "应用程序设置已成功保存")
        self.status_bar.showMessage("设置已保存", 3000)
    
    def _load_default_rules(self):
        """加载默认规则"""
        try:
            # 获取默认规则文件路径
            base_dir = Path(__file__).parent.parent.parent
            rules_path = base_dir / "config" / "default_rules.json"
            
            # 加载规则
            self.rule_manager.load_rules(rules_path)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"加载默认规则失败: {str(e)}")
    
    def _handle_rule_selected(self, rule_id):
        """处理选择规则事件"""
        # 切换到规则编辑选项卡
        self.tab_widget.setCurrentIndex(1)
        
        # 加载选中的规则
        rule = self.rule_manager.get_rule(rule_id)
        if rule:
            self.rule_editor_widget.load_rule(rule)
    
    def _handle_rule_added(self):
        """处理添加规则事件"""
        # 切换到规则编辑选项卡
        self.tab_widget.setCurrentIndex(1)
        
        # 清空编辑器以创建新规则
        self.rule_editor_widget.clear()
    
    def _handle_rule_saved(self):
        """处理保存规则事件"""
        # 更新规则列表
        self.rule_list_widget.refresh()
        
        # 显示状态消息
        self.status_bar.showMessage("规则已保存", 3000)
    
    def _create_new_rule(self):
        """创建新规则"""
        # 切换到规则编辑选项卡
        self.tab_widget.setCurrentIndex(1)
        
        # 清空编辑器
        self.rule_editor_widget.clear()
    
    def _open_config(self):
        """打开配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开配置文件", "", "JSON文件 (*.json)"
        )
        
        if file_path:
            if self.rule_manager.load_rules(file_path):
                # 刷新规则列表
                self.rule_list_widget.refresh()
                
                # 清空编辑器
                self.rule_editor_widget.clear()
                
                # 显示状态消息
                self.status_bar.showMessage(f"已加载配置: {file_path}", 3000)
            else:
                QMessageBox.warning(self, "加载失败", "无法加载配置文件")
    
    def _save_config(self):
        """保存配置文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", "", "JSON文件 (*.json)"
        )
        
        if file_path:
            if self.rule_manager.save_rules(file_path):
                # 显示状态消息
                self.status_bar.showMessage(f"已保存配置: {file_path}", 3000)
            else:
                QMessageBox.warning(self, "保存失败", "无法保存配置文件")
    
    def _export_script(self):
        """导出Bash脚本"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出Bash脚本", "", "Shell脚本 (*.sh)"
        )
        
        if file_path:
            if self.rule_manager.export_to_bash_script(file_path):
                # 显示状态消息
                self.status_bar.showMessage(f"已导出脚本: {file_path}", 3000)
                
                # 显示成功消息
                QMessageBox.information(
                    self, "导出成功", 
                    f"脚本已成功导出到: {file_path}\n\n"
                    "您可以将此脚本复制到目标系统使用。"
                )
            else:
                QMessageBox.warning(self, "导出失败", "无法导出脚本")
    
    def _delete_rule(self):
        """删除规则"""
        # 获取当前选中的规则
        rule_id = self.rule_list_widget.get_selected_rule_id()
        if rule_id is None:
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", 
            "确定要删除选中的规则吗？此操作无法撤销。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.rule_manager.delete_rule(rule_id):
                # 刷新规则列表
                self.rule_list_widget.refresh()
                
                # 清空编辑器
                self.rule_editor_widget.clear()
                
                # 显示状态消息
                self.status_bar.showMessage("规则已删除", 3000)
    
    def _toggle_rule(self):
        """启用/禁用规则"""
        # 获取当前选中的规则
        rule_id = self.rule_list_widget.get_selected_rule_id()
        if rule_id is None:
            return
        
        # 获取规则
        rule = self.rule_manager.get_rule(rule_id)
        if rule:
            # 切换启用状态
            rule.enabled = not rule.enabled
            
            # 刷新规则列表
            self.rule_list_widget.refresh()
            
            # 如果当前正在编辑该规则，则更新编辑器
            if self.rule_editor_widget.current_rule_id == rule_id:
                self.rule_editor_widget.load_rule(rule)
            
            # 显示状态消息
            status = "启用" if rule.enabled else "禁用"
            self.status_bar.showMessage(f"规则已{status}", 3000)
    
    def _duplicate_rule(self):
        """复制规则"""
        # 获取当前选中的规则
        rule_id = self.rule_list_widget.get_selected_rule_id()
        if rule_id is None:
            return
        
        # 获取规则
        rule = self.rule_manager.get_rule(rule_id)
        if rule:
            # 创建新规则
            new_rule = type(rule)(
                0,  # 新ID会在添加时自动分配
                f"{rule.name} (复制)",
                rule.description,
                rule.pattern,
                rule.action,
                rule.enabled,
                output=rule.output,
                script=rule.script,
                filter=rule.filter,
                condition=rule.condition
            )
            
            # 添加新规则
            new_id = self.rule_manager.add_rule(new_rule)
            
            # 刷新规则列表
            self.rule_list_widget.refresh()
            
            # 加载新规则到编辑器
            self.rule_editor_widget.load_rule(self.rule_manager.get_rule(new_id))
            
            # 切换到规则编辑选项卡
            self.tab_widget.setCurrentIndex(1)
            
            # 显示状态消息
            self.status_bar.showMessage("规则已复制", 3000)
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于", 
            "Linux命令伪装配置工具\n\n"
            "版本: 1.0.0\n"
            "这是一个用于创建和管理Linux命令伪装配置的工具，"
            "可以自定义规则以模拟特定命令的执行结果。"
        )
    
    def closeEvent(self, event):
        """关闭窗口事件"""
        # 询问是否保存更改
        reply = QMessageBox.question(
            self, "确认退出", 
            "是否保存当前规则配置？",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, 
            QMessageBox.Save
        )
        
        if reply == QMessageBox.Cancel:
            event.ignore()
        elif reply == QMessageBox.Save:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存配置文件", "", "JSON文件 (*.json)"
            )
            
            if file_path:
                self.rule_manager.save_rules(file_path)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
