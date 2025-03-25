"""
常量定义模块。
"""
import os

class CursorConstants:
    """
    Cursor应用程序常量类。
    """
    # 获取项目根目录路径
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

    # 资源目录路径
    RESOURCES_DIR = os.path.join(PROJECT_ROOT, 'resources', 'images')

    # 图标路径
    ICON_PATH = os.path.join(RESOURCES_DIR, 'icon', 'icon.png')

    CURSOR_PROCESS_NAME = "Cursor.exe"

    # 按钮图片名称
    SETTING_BUTTON_IMAGES = [
        "button/setting-button-light.png",
        "button/setting-button-dark.png"
    ]

    # manage按钮图片名称
    MANAGE_BUTTON_IMAGES = [
        "button/manage-button-light.png",
        "button/manage-button-dark.png"
    ]


    # 登录按钮图片名称
    SIGN_BUTTON_IMAGES = [
        "button/sign-button-light.png",
        "button/sign-button-dark.png"
    ]


    # 登出按钮图片名称
    LOGOUT_BUTTON_IMAGES = [
        "button/logout-button-light.png",
        "button/logout-button-dark.png"
    ]

    # Cursor可执行文件路径
    CURSOR_EXE_PATH = os.path.expandvars(
        r"%LOCALAPPDATA%\Programs\Cursor\Cursor.exe"
    )

    # Cursor认证数据路径
    CURSOR_AUTH_PATH = r"%APPDATA%\Cursor\User Data\Default\Local Storage\leveldb" 

    # Cursor setting url
    SURSOR_SETTINGS_URL = "https://www.cursor.com/cn/settings"

    # Cursor SIGN url
    SURSOR_SIGN_URL = "https://authenticator.cursor.sh"
