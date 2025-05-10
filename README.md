# Linux命令伪装配置工具

## 简介
这是一个基于PySide6开发的图形界面工具，用于创建和管理Linux命令伪装配置。该工具允许用户自定义规则，以模拟特定命令的执行结果，主要用于安全测试和环境模拟。

## 主要功能
- 支持自定义配置添加规则，集中管理输出
- 内置多种预定义规则模板（模拟安全策略、移除SUID、替换关键词等）
- 可视化编辑和管理规则
- 实时预览规则效果
- 导入/导出配置文件
- 支持自定义日志输出目录和文件名
- 支持扩展更多命令类型（如sh、bash、cat等）

## 技术栈
- Python 3.8+
- PySide6
- QSS样式表

## 项目结构
```
LinuxbaseTools/
├── README.md                    # 项目说明文档
├── main.py                      # 主程序入口
├── requirements.txt             # 项目依赖
├── .windsurfrules               # 项目规则文件
├── src/                         # 源代码目录
│   ├── core/                    # 核心功能模块
│   │   ├── __init__.py
│   │   ├── rule_manager.py      # 规则管理器
│   │   ├── rule_parser.py       # 规则解析器
│   │   └── mock_engine.py       # 命令模拟引擎
│   ├── ui/                      # 用户界面模块
│   │   ├── __init__.py
│   │   ├── main_window.py       # 主窗口
│   │   ├── rule_editor.py       # 规则编辑器
│   │   └── rule_list.py         # 规则列表
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   └── common.py            # 通用工具函数
│   └── resources/               # 资源文件
│       ├── styles/              # QSS样式表
│       │   └── main.qss         # 主样式表
│       └── icons/               # 图标资源
└── config/                      # 配置文件目录
    └── default_rules.json       # 默认规则配置
```

## 使用方法
1. 安装依赖：`pip install -r requirements.txt`
2. 运行程序：`python main.py`
3. 通过界面添加、编辑和管理伪装规则
4. 导出配置到目标系统使用

## 开发计划
- [ ] 基础UI界面实现
- [ ] 规则管理核心功能
- [ ] 规则导入/导出功能
- [ ] 规则测试与预览
- [ ] 更多命令类型支持
- [ ] 配置文件加密

## 许可证
MIT License
