"""
主应用程序模块。
"""
import tkinter as tk
from typing import NoReturn
from .ui.main_window import MainWindow

class CursorSekiroApp:
    """
    Cursor Sekiro应用程序类。
    """
    
    def __init__(self):
        """初始化应用程序。"""
        self.root = tk.Tk()
        self.main_window = MainWindow(self.root)
    
    def run(self) -> NoReturn:
        """运行应用程序。"""
        self.root.mainloop() 