import os
import pathlib

# 项目根目录
project_root = pathlib.Path(__file__).parent.absolute()

# 需要创建的目录结构
directories = [
    "src/core",
    "src/ui",
    "src/utils",
    "src/resources/styles",
    "src/resources/icons",
    "config"
]

# 创建目录
for directory in directories:
    dir_path = project_root / directory.replace('/', os.sep)
    os.makedirs(dir_path, exist_ok=True)
    print(f"创建目录: {dir_path}")

# 创建__init__.py文件以使包可导入
init_files = [
    "src/__init__.py",
    "src/core/__init__.py",
    "src/ui/__init__.py",
    "src/utils/__init__.py",
    "src/resources/__init__.py"
]

for init_file in init_files:
    file_path = project_root / init_file.replace('/', os.sep)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("# 自动生成的包初始化文件")
    print(f"创建文件: {file_path}")

# 创建.windsurfrules文件
rules_file = project_root / ".windsurfrules"
with open(rules_file, 'w', encoding='utf-8') as f:
    f.write("# 项目规则文件\n")
    f.write("1. 与用户用中文交流\n")
    f.write("2. 如果代码更新需要更新README.md\n")
    f.write("3. 主题相关文件需要统一管理，界面使用qss\n")
    f.write("4. 需要提示用户在.windsurfrules添加规则\n")
print(f"创建文件: {rules_file}")

print("项目目录结构创建完成!")
