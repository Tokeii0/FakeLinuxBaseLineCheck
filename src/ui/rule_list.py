from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView
)

from ..core.rule_manager import RuleManager


class RuleListWidget(QWidget):
    """规则列表组件"""
    
    # 自定义信号
    rule_selected = Signal(int)  # 规则ID
    rule_added = Signal()
    
    def __init__(self, rule_manager: RuleManager):
        super().__init__()
        
        self.rule_manager = rule_manager
        
        # 设置UI
        self._setup_ui()
        
        # 初始化表格数据
        self.refresh()
    
    def _setup_ui(self):
        """设置UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "名称", "描述", "类型", "状态"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置表格列宽
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # 连接信号
        self.table.itemDoubleClicked.connect(self._handle_item_double_clicked)
        
        main_layout.addWidget(self.table)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 添加规则按钮
        self.add_button = QPushButton("添加规则")
        self.add_button.clicked.connect(self._handle_add_button_clicked)
        button_layout.addWidget(self.add_button)
        
        # 编辑规则按钮
        self.edit_button = QPushButton("编辑规则")
        self.edit_button.clicked.connect(self._handle_edit_button_clicked)
        button_layout.addWidget(self.edit_button)
        
        # 删除规则按钮
        self.delete_button = QPushButton("删除规则")
        self.delete_button.clicked.connect(self._handle_delete_button_clicked)
        button_layout.addWidget(self.delete_button)
        
        # 启用/禁用规则按钮
        self.toggle_button = QPushButton("启用/禁用")
        self.toggle_button.clicked.connect(self._handle_toggle_button_clicked)
        button_layout.addWidget(self.toggle_button)
        
        # 设置布局右对齐
        button_layout.setAlignment(Qt.AlignRight)
        
        main_layout.addLayout(button_layout)
    
    def refresh(self):
        """刷新表格数据"""
        # 清空表格
        self.table.setRowCount(0)
        
        # 获取所有规则
        rules = self.rule_manager.get_all_rules()
        
        # 添加规则到表格
        for i, rule in enumerate(rules):
            self.table.insertRow(i)
            
            # 设置ID
            id_item = QTableWidgetItem(str(rule.id))
            self.table.setItem(i, 0, id_item)
            
            # 设置名称
            name_item = QTableWidgetItem(rule.name)
            self.table.setItem(i, 1, name_item)
            
            # 设置描述
            desc_item = QTableWidgetItem(rule.description)
            self.table.setItem(i, 2, desc_item)
            
            # 设置类型
            action_map = {
                'replace': '替换输出',
                'script': '自定义脚本',
                'filter': '过滤输出',
                'empty': '返回空'
            }
            action_text = action_map.get(rule.action, rule.action)
            action_item = QTableWidgetItem(action_text)
            self.table.setItem(i, 3, action_item)
            
            # 设置状态
            status_text = "启用" if rule.enabled else "禁用"
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(Qt.green if rule.enabled else Qt.red)
            self.table.setItem(i, 4, status_item)
    
    def get_selected_rule_id(self):
        """获取当前选中的规则ID"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        
        row = selected_items[0].row()
        id_item = self.table.item(row, 0)
        
        return int(id_item.text())
    
    def _handle_item_double_clicked(self, item):
        """处理双击表格项事件"""
        row = item.row()
        id_item = self.table.item(row, 0)
        rule_id = int(id_item.text())
        
        # 发送规则选中信号
        self.rule_selected.emit(rule_id)
    
    def _handle_add_button_clicked(self):
        """处理添加规则按钮点击事件"""
        # 发送规则添加信号
        self.rule_added.emit()
    
    def _handle_edit_button_clicked(self):
        """处理编辑规则按钮点击事件"""
        rule_id = self.get_selected_rule_id()
        if rule_id is not None:
            # 发送规则选中信号
            self.rule_selected.emit(rule_id)
    
    def _handle_delete_button_clicked(self):
        """处理删除规则按钮点击事件"""
        rule_id = self.get_selected_rule_id()
        if rule_id is not None:
            # 删除规则
            if self.rule_manager.delete_rule(rule_id):
                # 刷新表格
                self.refresh()
    
    def _handle_toggle_button_clicked(self):
        """处理启用/禁用规则按钮点击事件"""
        rule_id = self.get_selected_rule_id()
        if rule_id is not None:
            # 获取规则
            rule = self.rule_manager.get_rule(rule_id)
            if rule:
                # 切换启用状态
                rule.enabled = not rule.enabled
                
                # 刷新表格
                self.refresh()
