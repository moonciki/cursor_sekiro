"""
Cursor控制器模块,处理Cursor编辑器的核心操作。
"""
import os
import subprocess
import psutil
import shutil
from typing import Optional
from ..logger import Logger
from ..utils.constants import CursorConstants

class CursorController:
    """
    Cursor编辑器控制器类。
    """
    
    def __init__(self, logger: Logger):
        """
        初始化Cursor控制器。

        Args:
            logger: 日志管理器实例
        """
        self.logger = logger
        self.cursor_path = CursorConstants.CURSOR_EXE_PATH
        self.auth_path = CursorConstants.CURSOR_AUTH_PATH

    @staticmethod
    def is_cursor_running() -> bool:
        """
        检查Cursor编辑器是否正在运行。

        Returns:
            bool: 如果Cursor正在运行返回True,否则返回False
        """
        for proc in psutil.process_iter(['name']):
            try:
                if 'cursor' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def launch_cursor(self) -> None:
        """启动Cursor编辑器。"""
        try:
            if not self.is_cursor_running():
                os.startfile(CursorConstants.CURSOR_EXE_PATH)
                self.logger.log("已启动Cursor", "INFO")
            else:
                self.logger.log("Cursor已在运行", "INFO")
        except Exception as e:
            self.logger.log(f"启动Cursor失败: {str(e)}", "ERROR")

    def logout_cursor(self) -> None:
        """退出Cursor的登录状态。"""
        try:
            # 关闭Cursor进程
            for proc in psutil.process_iter(['name']):
                try:
                    if 'cursor' in proc.info['name'].lower():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 删除登录信息
            auth_path = os.path.expandvars(CursorConstants.CURSOR_AUTH_PATH)
            if os.path.exists(auth_path):
                shutil.rmtree(auth_path)
            
            self.logger.log("已退出Cursor登录", "INFO")
        except Exception as e:
            self.logger.log(f"退出Cursor登录失败: {str(e)}", "ERROR") 