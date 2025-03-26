"""
Cursor控制器模块,处理Cursor编辑器的核心操作。
"""
import os
import subprocess
import time
import psutil
import pyautogui
import pyperclip
from pyscreeze import Box
import win32com.client
import shutil
from typing import Optional, Tuple
from ..logger import Logger
from .cursor_constants import CursorConstants
import win32gui
import win32process
import win32con
import pythoncom

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
        pythoncom.CoInitialize()
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
        pythoncom.CoInitialize()
        wmi = win32com.client.GetObject("winmgmts:")
        processes = wmi.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{process_name}'")
        # 只获取第一个进程的PID
        for process in processes:
            return process.Properties_("ProcessID").Value
        return None  # 如果没有找到进程则返回None



    @staticmethod
    def focus_pid_window(pid) -> bool:
        """
        聚焦指定PID的窗口
        
        Args:
            pid: 进程ID
        """
        try:
            # 获取所有窗口
            windows = gw.getAllWindows()
            
            for window in windows:
                try:
                    # 获取窗口的PID - 修复方法
                    window_handle = window._hWnd  # 获取窗口句柄
                    _, window_pid = win32process.GetWindowThreadProcessId(window_handle)
                    
                    if window_pid == pid:
                        Logger.info(f"找到匹配的窗口: {window.title}")
                        window.activate()
                        return True
                except Exception as e:
                    Logger.error(f"处理窗口时出错: {str(e)}")
                    continue
            
            Logger.warn(f"未找到PID为{pid}的窗口")
            return False
            
        except Exception as e:
            Logger.error(f"聚焦窗口失败: {str(e)}")
            return False



    
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
    def paste_text(text: str):
        """
        粘贴文字到当前活动窗口
        
        Args:
            text: 要粘贴的文字
        """
        # 使用剪贴板方式输入，避免输入法问题
        pyperclip.copy(text)  # 复制文字到剪贴板
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')  # 粘贴
        time.sleep(0.3)



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
    def loop_click_button_multi(search_region: Tuple[int, int, int, int], *button_images: str, tryCount: int) -> bool:
        """
        尝试多次点击多个按钮图片中的任意一个，直到尝试次数用完或成功点击。

        Args:
            search_region: 搜索区域的坐标 (left, top, width, height)
            button_images: 要查找的按钮图片路径列表
            tryCount: 尝试点击的最大次数

        Returns:
            bool: 是否成功点击了任意一个按钮
        """
        for attempt in range(tryCount):
            Logger.info(f"尝试点击按钮，第 {attempt+1}/{tryCount} 次")
            
            
            if WindowTools.loop_click_button_once(search_region, *button_images):
                Logger.info(f"成功点击按钮，尝试次数: {attempt+1}")
                return True

            time.sleep(1)  # 每次尝试之间稍作等待
            
        Logger.info(f"尝试 {tryCount} 次后未能成功点击任何按钮")
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

