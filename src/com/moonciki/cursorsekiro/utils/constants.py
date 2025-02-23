"""
常量定义模块。
"""
import os

# 获取项目根目录路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

# 资源目录路径
RESOURCES_DIR = os.path.join(PROJECT_ROOT, 'resources', 'images')

# 图标路径
ICON_PATH = os.path.join(RESOURCES_DIR, 'icon', 'icon.png')  # 使用正确的相对路径

# 按钮图片名称
SETTING_BUTTON_IMAGES = [
    "button/setting-button-light.png",
    "button/setting-button-dark.png"
]

# Cursor可执行文件路径
CURSOR_EXE_PATH = 'C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Cursor\\Cursor.exe'

# Cursor认证数据路径
CURSOR_AUTH_PATH = r"%APPDATA%\Cursor\User Data\Default\Local Storage\leveldb" 