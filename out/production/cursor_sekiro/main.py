"""
程序入口点模块。
包含管理员权限检查和程序启动逻辑。
"""
import sys
import ctypes
from tkinter import messagebox

from com.moonciki.cursorsekiro.app import CursorSekiroApp

def is_admin() -> bool:
    """
    检查当前程序是否以管理员权限运行。
    
    Returns:
        bool: 如果是管理员权限返回True，否则返回False
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main() -> None:
    """
    程序入口点。
    检查管理员权限，如果不是管理员则显示提示信息并退出。
    """
    if not is_admin():
        messagebox.showerror(
            "需要管理员权限",
            "请以管理员身份运行此程序。\n"
            "请右键点击程序，选择'以管理员身份运行'。"
        )
        sys.exit(1)

    # 以管理员权限运行程序
    app = CursorSekiroApp()
    app.run()

if __name__ == "__main__":
    main() 
    