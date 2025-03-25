"""
Cursor控制器模块,处理Cursor编辑器的核心操作。
"""
import os
import subprocess
import time
import psutil
import pyautogui
import win32com.client
import shutil
from typing import Optional, Tuple
from ..logger import Logger
from .constants import CursorConstants
import win32gui
import win32process
import win32con

import pygetwindow as gw

class WindowTools:
    """
    windows控制器类。
    """
    
    @staticmethod
    def is_process_running(process_name) -> bool:
        """
        使用 WMI 查询 process_name 进程是否存在。
        """
        wmi = win32com.client.GetObject("winmgmts:")
        processes = wmi.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{process_name}'")

        runResult = (len(processes) > 0)
        Logger.info(f"{process_name} 进程数量： {runResult}");

        return runResult


    @staticmethod
    def get_pid_by_process_name(process_name: str):
        """
        根据进程名称获取 PID。

        Args:
            process_name (str): 进程名称（如 "Cursor.exe"）。

        Returns:
            list: 包含所有匹配进程的 PID 列表。
        """
        wmi = win32com.client.GetObject("winmgmts:")
        processes = wmi.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{process_name}'")
        pidText = [process.Properties_("ProcessID").Value for process in processes]
        return pidText[0] if pidText else None  # 返回第一个PID，如果没有找到则返回None



    @staticmethod
    def focus_pid_window(pid):
        # 获取所有窗口
        windows = gw.getAllWindows()
        for window in windows:
            if window._hWnd:  # 检查窗口句柄是否存在
                # 获取窗口的进程 ID
                window_pid = window.getOwnerId()
                if window_pid == pid:
                    # 激活窗口
                    window.activate()
                    print(f"Focused window with PID: {pid}")
                    return
        print(f"No window found with PID: {pid}")



    
    @staticmethod
    def capture_region_image(search_region: Tuple[int, int, int, int]) -> bool:
        """
        抓取区域图片，并保存至 tmp 目录下。
        
        Args:
            search_region: 要截图的区域坐标 (left, top, width, height)
            
        Returns:
            bool: 截图是否成功
        """
        try:
            # 确保tmp目录存在
            tmp_dir = os.path.join(CursorConstants.PROJECT_ROOT, "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            
            # 生成截图文件路径
            timestamp = int(time.time())
            screenshot_path = os.path.join(tmp_dir, f"region_{timestamp}.png")
            
            # 截取指定区域的图片
            screenshot = pyautogui.screenshot(region=search_region)
            screenshot.save(screenshot_path)
            
            Logger.info(f"区域截图已保存至: {screenshot_path}")
            return True
            
        except Exception as e:
            Logger.error(f"区域截图失败: {str(e)}")
            return False


    @staticmethod
    def loop_click_button_once(search_region: Tuple[int, int, int, int], *button_images: str) -> bool:
        """
        尝试点击多个按钮图片中的任意一个。当找到并点击成功一个后立即返回。

        Args:
            search_region: 搜索区域的坐标 (left, top, width, height)
            button_images: 要查找的按钮图片路径列表

        Returns:
            bool: 是否成功点击了任意一个按钮
        """
        for image in button_images:
            if WindowTools._click_single_button(image, search_region):
                return True
        return False 



    @staticmethod
    def _click_single_button(button_image_name: str, search_region: Tuple[int, int, int, int]) -> bool:
        """
        在Cursor编辑器中查找并点击指定的按钮。

        Args:
            button_image_name: 按钮图像的文件名
            search_region: 搜索区域的坐标 (left, top, width, height)
        
        Returns:
            bool: 是否成功点击按钮
        """
        try:
            button_image_path = os.path.join(CursorConstants.RESOURCES_DIR, button_image_name)
            
            if not os.path.exists(button_image_path):
                Logger.error(f"按钮图片不存在: {button_image_path}")
                return False
                
            window = gw.getActiveWindow()
            if not window or 'cursor' not in window.title.lower():
                Logger.warn("当前窗口不是Cursor")
                return False

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
                        pyautogui.moveTo(button_center.x, button_center.y)
                        pyautogui.click()
                        Logger.info("成功点击按钮")
                        return True
                
                return False
                
            except Exception as e:
                import traceback
                print(f"异常类型: {e.__class__.__name__}")
                print(f"异常信息: {str(e)}")
                print("异常堆栈:")
                print(traceback.format_exc())
                Logger.warn(f"查找按钮失败: {str(e)}")
                return False
            
        except Exception as e:
            Logger.error(f"点击按钮失败: {str(e)}")
            return False

