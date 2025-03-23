"""
窗口操作模块,处理Cursor窗口的操作。
"""
import time
import psutil
import win32com.client
import win32gui
import win32process
import win32con
import pyautogui
import pygetwindow as gw
import os
from typing import Optional, Tuple
from ..logger import Logger
from ..utils.constants import CursorConstants
from PIL import Image
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowController:
    """
    窗口控制器类。
    """
    
    def __init__(self):
        """
        初始化窗口控制器。
        """
        # 设置pyautogui的安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5

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

    def focus_cursor_window(self) -> None:
        """聚焦Cursor窗口。"""
        try:
            pid = self.get_pid_by_process_name(CursorConstants.CURSOR_PROCESS_NAME)

            # 判断是否找到 Cursor 进程
            if not pid:
                Logger.error("未找到 Cursor 进程")
                return
            
            Logger.info(f"找到 Cursor 进程，PID: {pid}")

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
                Logger.info("已成功聚焦Cursor窗口")
                return
        
        except Exception as e:
            Logger.error(f"聚焦Cursor窗口失败: {str(e)}")

    def capture_region_image(self, search_region: Tuple[int, int, int, int]) -> bool:
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

    def click_cursor_setting(self) -> bool:
        """点击Cursor设置按钮"""
        window = gw.getActiveWindow()
        if not window or 'cursor' not in window.title.lower():
            Logger.warn("当前窗口不是Cursor")
            return False
        
        # 设置按钮通常在右上角
        search_region = (
            max(0, window.right - 800),
            max(0, window.top),
            min(800, window.right),
            min(300, window.height)
        )
        
        return self.loop_click_button_once(search_region, *CursorConstants.SETTING_BUTTON_IMAGES)


    def click_cursor_manager(self) -> bool:
        """点击Cursor manager按钮"""
        window = gw.getActiveWindow()
        if not window or 'cursor' not in window.title.lower():
            Logger.warn("当前窗口不是Cursor")
            return False
            
        # 登出按钮通常在整个窗口范围内
        search_region = (
            max(0, window.left),
            max(0, window.top), 
            max(0, window.width),
            max(0, window.height)
        )
        
        self.capture_region_image(search_region)

        return self.loop_click_button_once(search_region, *CursorConstants.MANAGE_BUTTON_IMAGES)


    def click_cursor_sign(self) -> bool:
        """点击Cursor sign按钮"""
        window = gw.getActiveWindow()
        if not window or 'cursor' not in window.title.lower():
            Logger.warn("当前窗口不是Cursor")
            return False
            
        # 登出按钮通常在整个窗口范围内
        search_region = (
            max(0, window.left),
            max(0, window.top), 
            max(0, window.width),
            max(0, window.height)
        )
        
        self.capture_region_image(search_region)

        return self.loop_click_button_once(search_region, *CursorConstants.SIGN_BUTTON_IMAGES)

    def click_cursor_logout(self) -> bool:
        """点击Cursor登出按钮"""
        window = gw.getActiveWindow()
        if not window or 'cursor' not in window.title.lower():
            Logger.warn("当前窗口不是Cursor")
            return False
            
        # 登出按钮通常在整个窗口范围内
        search_region = (
            max(0, window.left),
            max(0, window.top), 
            max(0, window.width),
            max(0, window.height)
        )
        
        self.capture_region_image(search_region)

        return self.loop_click_button_once(search_region, *CursorConstants.LOGOUT_BUTTON_IMAGES)

    def _click_single_button(self, button_image_name: str, search_region: Tuple[int, int, int, int]) -> bool:
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

    def loop_click_button_once(self, search_region: Tuple[int, int, int, int], *button_images: str) -> bool:
        """
        尝试点击多个按钮图片中的任意一个。当找到并点击成功一个后立即返回。

        Args:
            search_region: 搜索区域的坐标 (left, top, width, height)
            button_images: 要查找的按钮图片路径列表

        Returns:
            bool: 是否成功点击了任意一个按钮
        """
        for image in button_images:
            if self._click_single_button(image, search_region):
                return True
        return False 