"""
主窗口UI模块。
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import time
from typing import Callable
from ..logger import Logger
from ..cursor.controller import CursorController
from ..cursor.window import WindowController
from ..utils.constants import CursorConstants

class MainWindow:
    """
    主窗口类,处理UI相关操作。
    """
    
    def __init__(self, root: tk.Tk):
        """
        初始化主窗口。

        Args:
            root: Tkinter根窗口实例
        """
        self.root = root
        self.root.title("Cursor Sekiro")
        self.root.geometry("600x500")
        
        # 先初始化必要的属性
        self.status_label = None
        self.cursor_controller = None
        self.window_controller = None
        
        # 创建日志组件但不立即显示
        self.log_widget = scrolledtext.ScrolledText(
            self.root,
            height=10,
            font=("Courier", 10),
            state='disabled'
        )
        self.logger = Logger(self.log_widget)
        
        # 加载图标 - 静默处理错误
        try:
            if os.path.exists(CursorConstants.ICON_PATH):
                icon = tk.PhotoImage(file=CursorConstants.ICON_PATH)
                self.root.iconphoto(True, icon)
        except Exception:
            pass
        
        # 设置UI
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """设置用户界面组件。"""
        # 创建上半部分的Frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建主标签
        main_label = tk.Label(
            top_frame,
            text="Hello World!",
            font=("Arial", 24)
        )
        main_label.pack(expand=True, pady=10)
        
        # 创建状态标签
        self.status_label = tk.Label(
            top_frame,
            text="点击按钮检查Cursor状态",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        # 创建按钮Frame和按钮
        self._create_buttons(top_frame)
        
        # 创建日志区域
        self._create_log_area()
        
        # 初始化控制器
        self.cursor_controller = CursorController(self.logger)
        self.window_controller = WindowController(self.logger)

    def _create_buttons(self, parent: tk.Frame) -> None:
        """创建按钮区域"""
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=5)
        
        # 检查状态按钮
        tk.Button(
            button_frame,
            text="检查Cursor状态",
            command=self._check_cursor_status,
            font=("Arial", 12)
        ).pack(side=tk.LEFT, padx=5)
        
        # Evil按钮
        tk.Button(
            button_frame,
            text="Evil",
            command=self._launch_cursor,
            font=("Arial", 12),
            fg="red"
        ).pack(side=tk.LEFT, padx=5)
        
        # 登出按钮
        tk.Button(
            button_frame,
            text="退出Cursor登录",
            command=self._logout_cursor,
            font=("Arial", 12),
            fg="blue"
        ).pack(side=tk.LEFT, padx=5)
        
        # 设置按钮
        tk.Button(
            button_frame,
            text="Cursor设置",
            command=self._open_cursor_settings,
            font=("Arial", 12),
            fg="green"
        ).pack(side=tk.LEFT, padx=5)

    def _create_log_area(self) -> None:
        """创建日志区域"""
        log_control_frame = tk.Frame(self.root)
        log_control_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(
            log_control_frame,
            text="操作日志",
            font=("Arial", 12)
        ).pack(side=tk.LEFT, pady=(10, 5))
        
        tk.Button(
            log_control_frame,
            text="清除日志",
            command=self._clear_logs,
            font=("Arial", 10)
        ).pack(side=tk.RIGHT, pady=(10, 5))
        
        # 在这里显示日志组件
        self.log_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.logger.log("应用程序启动")

    def _check_cursor_status(self) -> None:
        """检查Cursor状态"""
        is_running = self.cursor_controller.is_cursor_running()
        status_text = "Cursor编辑器正在运行" if is_running else "Cursor编辑器未运行"
        self.status_label.config(text=status_text)
        self.logger.log(f"检查Cursor状态: {status_text}")

    def _launch_cursor(self) -> None:
        """启动Cursor"""
        self.cursor_controller.launch_cursor()

    def _logout_cursor(self) -> None:
        """退出Cursor登录"""
        try:
            # 先尝试通过UI点击登出
            if self.window_controller.click_logout_button():
                time.sleep(1)  # 等待登出操作完成
            
            # 无论UI操作是否成功,都执行强制登出
            self.cursor_controller.logout_cursor()
            
        except Exception as e:
            self.logger.log(f"登出操作失败: {str(e)}", "ERROR")

    def _clear_logs(self) -> None:
        """清除日志"""
        self.logger.clear()

    def _open_cursor_settings(self) -> None:
        """打开Cursor设置"""
        try:
            result = messagebox.showwarning(
                "操作提示",
                "激活过程中，请勿操作电脑",
                icon='warning'
            )
            
            if result == 'ok':
                self.logger.log("开始打开Cursor设置流程", "INFO")
                
                if not self.cursor_controller.is_cursor_running():
                    self.logger.log("Cursor未运行，正在启动...", "INFO")
                    self.cursor_controller.launch_cursor()
                    time.sleep(5)
                
                self.window_controller.focus_cursor_window()
                time.sleep(1)
                
                self.window_controller.click_cursor_setting()
                time.sleep(1)
                
                self.window_controller.click_cursor_logout()
                time.sleep(1)
                
                self.logger.log("打开设置成功", "INFO")
                
                
        except Exception as e:
            self.logger.log(f"打开设置失败: {str(e)}", "ERROR") 