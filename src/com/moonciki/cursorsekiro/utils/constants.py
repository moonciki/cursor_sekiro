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

    # 登录页面，点击其他位置，使输入框失去焦点
    CHROME_SIGN_BLUR_IMAGES = [
        "button/chrome-sign-blur.png"
    ]
    # 设置页面标识
    CHROME_SETTING_PAGE_IMG = [
        "button/chrome-setting-page.png"
    ]
    # 高级按钮
    CHROME_ADVANCE_IMAGE = [
        "button/chrome-advance-button.png"
    ]
    # 删除按钮
    CHROME_ADVANCE_DELETE_IMAGE = [
        "button/chrome-del-button.png"
    ]
    # 确认输入框
    CHROME_INPUT_CONFIRM_IMAGE = [
        "button/chrome-input-confirm.png"
    ]
    # 确认删除按钮
    CHROME_BTN_DELETE_CONFIRM = [
        "button/chrome-btn-delete-confirm.png"
    ]

    # 发送登录验证码
    CHROME_BTN_EMAIL_CODE_IMAGE = [
        "button/chrome-btn-email-code.png"
    ]

    # 发送登录验证码机器人校验
    CHROME_BTN_ROBOT_CHECK_IMAGE = [
        "button/chrome-btn-robot-check.png"
    ]
    # 发送登录验证码机器人校验
    CHROME_PAGE_ENTER_CODE = [
        "button/chrome-page-enter-code.png"
    ]

    
    # 密码框
    CHROME_INPUT_PASSWORD = [
        "button/chrome-input-password.png"
    ]

    # 全部已读
    CHROME_BTN_ALL_READ = [
        "button/chrome-btn-all-read.png"
    ]

    # Cursor可执行文件路径
    CURSOR_EXE_PATH = os.path.expandvars(
        r"%LOCALAPPDATA%\Programs\Cursor\Cursor.exe"
    )

    # 收信按钮
    CHROME_BTN_RECEIVE_EMAIL = [
        "button/chrome-btm-receive-email.png"
    ]

    # 新邮件按钮
    CHROME_BTN_NEW_EMAIL = [
        "button/chrome-btn-new-email.png"
    ]

    # 邮件内容
    CHROME_EMAIL_CONTENT = [
        "button/chrome-text-email-content.png"
    ]

    # Cursor认证数据路径
    CURSOR_AUTH_PATH = r"%APPDATA%\Cursor\User Data\Default\Local Storage\leveldb" 

    # Cursor setting url
    SURSOR_SETTINGS_URL = "https://www.cursor.com/cn/settings"

    # Cursor SIGN url
    SURSOR_SIGN_URL = "https://authenticator.cursor.sh"

    
    # 126 email url
    EMAIL_126_URL = "https://mail.126.com/"



