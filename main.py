#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from src.ui.main_window import MainWindow
from src.utils.common import load_stylesheet


def main():
    """主程序入口"""
    # 创建应用程序
    app = QApplication(sys.argv)
    app.setApplicationName("Linux命令伪装配置工具")
    
    # 设置应用程序样式
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 应用程序主循环
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
