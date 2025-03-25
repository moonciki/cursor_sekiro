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
    
    # 定义日志级别对应的颜色
    LOG_COLORS = {
        "INFO": "#00FF00",  # 绿色
        "WARN": "#FFA500",  # 橙色
        "ERROR": "#FF0000"  # 红色
    }
    
    log_widget = None
    
    def __init__(self, log_widget: scrolledtext.ScrolledText) -> None:
        """
        初始化日志管理器。

        Args:
            log_widget: 用于显示日志的文本组件
        """
        Logger.log_widget = log_widget
        Logger.log_widget.config(
            state='disabled',
            background='black',  # 设置黑色背景
            foreground='white'   # 设置默认文字颜色为白色
        )
    
    @staticmethod
    def _log(message: str, level: str) -> None:
        """
        内部日志记录方法。

        Args:
            message: 日志消息内容
            level: 日志级别
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        Logger.log_widget.config(state='normal')
        Logger.log_widget.insert(tk.END, log_message)
        
        # 获取最后插入的行的起始和结束位置
        last_line_start = Logger.log_widget.get("end-2c linestart", "end-1c")
        line_start = f"end-{len(last_line_start)}c linestart"
        
        # 为整行设置颜色
        Logger.log_widget.tag_add(level, line_start, "end-1c")
        Logger.log_widget.tag_config(level, foreground=Logger.LOG_COLORS[level])
        
        Logger.log_widget.see(tk.END)
        Logger.log_widget.config(state='disabled')
    
    @staticmethod
    def info(message: str) -> None:
        """
        记录信息级别的日志消息。

        Args:
            message: 日志消息内容
        """
        Logger._log(message, "INFO")
    
    @staticmethod
    def warn(message: str) -> None:
        """
        记录警告级别的日志消息。

        Args:
            message: 日志消息内容
        """
        Logger._log(message, "WARN")
    
    @staticmethod
    def error(message: str) -> None:
        """
        记录错误级别的日志消息。

        Args:
            message: 日志消息内容
        """
        Logger._log(message, "ERROR")
    
    @staticmethod
    def error(message: str, exception: Exception = None) -> None:
        """
        记录错误级别的日志消息。

        Args:
            message: 日志消息内容
            exception: 可选的异常对象,将记录其堆栈信息
        """
        Logger._log(message, "ERROR")
        if exception:
            import traceback
            stack_trace = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            Logger._log(f"异常堆栈:\n{stack_trace}", "ERROR")

    @staticmethod
    def clear() -> None:
        """清除所有日志内容。"""
        Logger.log_widget.config(state='normal')
        Logger.log_widget.delete(1.0, tk.END)
        Logger.log_widget.config(state='disabled')
        Logger.info("日志已清除") 