import os
import sys
from pathlib import Path


def get_app_root():
    """获取应用程序根目录"""
    # 如果是作为PyInstaller打包的可执行文件
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    
    # 如果是作为Python脚本运行
    return Path(__file__).parent.parent.parent


def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    base_path = get_app_root()
    return base_path / relative_path


def ensure_directory_exists(path):
    """确保目录存在，如果不存在则创建"""
    os.makedirs(path, exist_ok=True)


def get_config_dir():
    """获取配置目录"""
    config_dir = get_resource_path("config")
    ensure_directory_exists(config_dir)
    return config_dir


def get_default_rules_path():
    """获取默认规则文件路径"""
    return get_config_dir() / "default_rules.json"


def get_user_rules_path():
    """获取用户规则文件路径"""
    return get_config_dir() / "user_rules.json"


def get_style_path():
    """获取样式表文件路径"""
    return get_resource_path("src/resources/styles/main.qss")


def load_stylesheet():
    """加载样式表"""
    try:
        style_path = get_style_path()
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    except Exception as e:
        print(f"加载样式表失败: {str(e)}")
        return ""
