"""
常量定义模块。
"""
import os
import sys
import pyautogui

class CursorConstants:
    """
    Cursor应用程序常量类。
    """
    # 获取项目根目录路径（兼容打包环境）
    @staticmethod
    def get_project_root():
        """获取项目根目录，兼容开发环境和打包环境"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的应用程序
            return os.path.dirname(sys.executable)
        else:
            # 如果是开发环境，使用原来的方法
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))
    
    # 使用静态方法获取项目根目录
    PROJECT_ROOT = get_project_root.__func__()

    # 配置文件路径
    CONFIG_FILE_PATH = os.path.join(
        PROJECT_ROOT, 
        "config", 
        "email_config.json"
    )

    # 资源目录路径
    RESOURCES_DIR = os.path.join(PROJECT_ROOT, 'resources', 'images')

    # 图标路径
    ICON_PATH = os.path.join(RESOURCES_DIR, 'icon', 'cursor-sekiro.ico')

    CURSOR_PROCESS_NAME = "Cursor.exe"

    # 获取屏幕宽高
    SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

    # 定义类变量
    CURSOR_PROCESS_NAMES = [
        "Cursor.exe",
        "cursor.exe",
        "cursor-updater.exe"
    ]

    # 按钮图片名称
    SETTING_BUTTON_IMAGES = [
        "button/cursor/setting-button-light.png",
        "button/cursor/setting-button-dark.png"
    ]

    # manage按钮图片名称
    MANAGE_BUTTON_IMAGES = [
        "button/cursor/manage-button-light.png",
        "button/cursor/manage-button-dark.png"
    ]


    # 登录按钮图片名称
    SIGN_BUTTON_IMAGES = [
        "button/cursor/sign-button-light.png",
        "button/cursor/sign-button-dark.png"
    ]


    # 登出按钮图片名称
    LOGOUT_BUTTON_IMAGES = [
        "button/cursor/logout-button-light.png",
        "button/cursor/logout-button-dark.png"
    ]

    # 登录页面，点击其他位置，使输入框失去焦点
    CHROME_SIGN_BLUR_IMAGES = [
        "button/chrome_cursor/chrome-sign-blur.png"
    ]
    # 设置页面标识
    CHROME_SETTING_PAGE_IMG = [
        "button/chrome_cursor/chrome-setting-page.png"
    ]
    # 高级按钮
    CHROME_ADVANCE_IMAGE = [
        "button/chrome_cursor/chrome-advance-button.png"
    ]
    # 删除按钮
    CHROME_ADVANCE_DELETE_IMAGE = [
        "button/chrome_cursor/chrome-del-button.png"
    ]
    # 确认输入框
    CHROME_INPUT_CONFIRM_IMAGE = [
        "button/chrome_cursor/chrome-input-confirm.png"
    ]
    # 确认删除按钮
    CHROME_BTN_DELETE_CONFIRM = [
        "button/chrome_cursor/chrome-btn-delete-confirm.png"
    ]

    # 发送登录验证码
    CHROME_BTN_EMAIL_CODE_IMAGE = [
        "button/chrome_cursor/chrome-btn-email-code.png"
    ]

    # 发送登录验证码机器人校验
    CHROME_BTN_ROBOT_CHECK_IMAGE = [
        "button/chrome_cursor/chrome-btn-robot-check.png"
    ]
    # 发送登录验证码机器人校验
    CHROME_PAGE_ENTER_CODE = [
        "button/chrome_cursor/chrome-page-enter-code.png"
    ]
    # 确认登录
    CHROME_BTN_LOGIN_SURE = [
        "button/chrome_cursor/chrome-btn-login-sure.png"
    ]
    
    
    # 密码框
    CHROME_INPUT_PASSWORD = [
        "button/chrome_cursor/chrome-input-password.png"
    ]

    # 全部已读
    CHROME_BTN_ALL_READ = [
        "button/chrome_email/chrome-btn-all-read.png"
    ]

    # 收信按钮
    CHROME_BTN_RECEIVE_EMAIL = [
        "button/chrome_email/chrome-btm-receive-email.png"
    ]

    # 新邮件按钮
    CHROME_BTN_NEW_EMAIL = [
        "button/chrome_email/chrome-btn-new-email.png"
    ]

    # 邮件内容
    CHROME_TEXT_EMAIL_CONTENT_START = [
        "button/chrome_email/chrome_text_email_content_start.png"
    ]

    # 邮件内容
    CHROME_TEXT_EMAIL_CONTENT_END = [
        "button/chrome_email/chrome_text_email_content_end.png"
    ]

    # 邮件内容
    CHROME_EMAIL_CONTENT = [
        "button/chrome_email/chrome-text-email-content.png"
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

    
    # 126 email url
    EMAIL_126_URL = "https://mail.126.com/"

