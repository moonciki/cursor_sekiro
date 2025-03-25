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

from com.moonciki.cursorsekiro.utils import WindowTools
from ..logger import Logger
from ..utils.constants import CursorConstants
from ..utils.WindowTools import WindowTools

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

    def focus_cursor_window() -> None:
        """聚焦Cursor窗口。"""

        pid = WindowTools.get_pid_by_process_name(CursorConstants.CURSOR_PROCESS_NAME)

        # 判断是否找到 Cursor 进程
        if not pid:
            Logger.error("未找到 Cursor 进程")
            return
        
        Logger.info(f"找到 Cursor 进程，PID: {pid}")
        
        WindowTools.focus_pid_window()

    def click_cursor_setting() -> bool:
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
        
        return WindowTools.loop_click_button_once(search_region, *CursorConstants.SETTING_BUTTON_IMAGES)


    def click_cursor_manager() -> bool:
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

        return WindowTools.loop_click_button_once(search_region, *CursorConstants.MANAGE_BUTTON_IMAGES)


    def click_cursor_sign() -> bool:
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
        
        return WindowTools.loop_click_button_once(search_region, *CursorConstants.SIGN_BUTTON_IMAGES)

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

