"""
日志管理模块,用于处理日志记录和显示。
"""
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
from typing import Optional

class Logger:
    """
    日志管理器类,用于处理日志记录和显示。
    
    Attributes:
        log_widget (scrolledtext.ScrolledText): 日志显示组件
    """
    
    def __init__(self, log_widget: scrolledtext.ScrolledText) -> None:
        """
        初始化日志管理器。

        Args:
            log_widget: 用于显示日志的文本组件
        """
        self.log_widget = log_widget
        self.log_widget.config(state='disabled')
    
    def log(self, message: str, level: str = "INFO") -> None:
        """
        记录一条日志消息。

        Args:
            message: 日志消息内容
            level: 日志级别,默认为"INFO"
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, log_message)
        self.log_widget.see(tk.END)
        self.log_widget.config(state='disabled')
    
    def clear(self) -> None:
        """清除所有日志内容。"""
        self.log_widget.config(state='normal')
        self.log_widget.delete(1.0, tk.END)
        self.log_widget.config(state='disabled')
        self.log("日志已清除") 