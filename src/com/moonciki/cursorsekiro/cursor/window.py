"""
窗口操作模块,处理Cursor窗口的操作。
"""
import time
import psutil
import win32gui
import win32process
import win32con
import pyautogui
import pygetwindow as gw
import os
from typing import Optional, Tuple
from ..logger import Logger
from ..utils.constants import RESOURCES_DIR

class WindowController:
    """
    窗口控制器类。
    """
    
    def __init__(self, logger: Logger):
        """
        初始化窗口控制器。

        Args:
            logger: 日志管理器实例
        """
        self.logger = logger
        # 设置pyautogui的安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

    def focus_cursor_window(self) -> None:
        """聚焦Cursor窗口。"""
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if 'cursor' in proc.info['name'].lower():
                        pid = proc.info['pid']
                        
                        def callback(hwnd, hwnds):
                            if win32gui.IsWindowVisible(hwnd):
                                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                                if found_pid == pid:
                                    hwnds.append(hwnd)
                            return True
                            
                        hwnds = []
                        win32gui.EnumWindows(callback, hwnds)
                        
                        if hwnds:
                            hwnd = hwnds[0]
                            if win32gui.IsIconic(hwnd):
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                            win32gui.SetForegroundWindow(hwnd)
                            self.logger.log("已成功聚焦Cursor窗口", "INFO")
                            return
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            self.logger.log("未找到Cursor窗口", "ERROR")
            
        except Exception as e:
            self.logger.log(f"聚焦Cursor窗口失败: {str(e)}", "ERROR")

    def click_cursor_button(self, button_image_name: str) -> bool:
        """
        在Cursor编辑器中查找并点击指定的按钮。

        Args:
            button_image_name: 按钮图像的文件名
        
        Returns:
            bool: 是否成功点击按钮
        """
        try:
            button_image_path = os.path.join(RESOURCES_DIR, button_image_name)
            
            if not os.path.exists(button_image_path):
                self.logger.log(f"按钮图片不存在: {button_image_path}", "ERROR")
                return False
                
            window = gw.getActiveWindow()
            if not window or 'cursor' not in window.title.lower():
                self.logger.log("当前窗口不是Cursor", "WARNING")
                return False
            
            search_region = (
                max(0, window.right - 800),
                max(0, window.top),
                min(800, window.right),
                min(200, window.height)
            )

            try:
                button_location = pyautogui.locateOnScreen(
                    button_image_path,
                    confidence=0.8,
                    region=search_region
                )
                
                if button_location:
                    button_center = pyautogui.center(button_location)
                    if (window.left <= button_center.x <= window.right and 
                        window.top <= button_center.y <= window.bottom):
                        pyautogui.moveTo(button_center.x, button_center.y, duration=0.2)
                        pyautogui.click()
                        self.logger.log("成功点击设置按钮", "INFO")
                        return True
                
                return False
                
            except Exception as e:
                self.logger.log(f"查找按钮失败: {str(e)}", "WARNING")
                return False
            
        except Exception as e:
            self.logger.log(f"点击按钮失败: {str(e)}", "ERROR")
            return False 