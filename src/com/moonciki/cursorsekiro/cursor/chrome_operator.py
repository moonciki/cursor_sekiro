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

import tkinter as tk
from PIL import Image
import logging


class ChromeOperator:
    """
    chrome窗口控制器类。
    """
    
    def __init__(self):
        """
        初始化窗口控制器。
        """
        # 设置pyautogui的安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5


    def check_chrome_open(self):
        """判断是否是chrome"""


        #循环判断是否有chrome 
        # 循环检查Chrome浏览器是否打开,最多等待15秒
        wait_time = 0
        while wait_time < 15:
            active_window = gw.getActiveWindow()
            if active_window and 'chrome' in active_window.title.lower():
                Logger.info("Chrome浏览器已打开")

                # 检查窗口是否已经最大化，如果没有则最大化
                if not active_window.isMaximized:
                    active_window.maximize()
                    Logger.info("Chrome浏览器已最大化")
                    time.sleep(0.5)  # 等待最大化完成
                else:
                    Logger.info("Chrome浏览器已经处于最大化状态")

                break
            time.sleep(2)
            wait_time += 1
            Logger.info(f"等待Chrome浏览器打开... {wait_time}秒")
        else:
            error_msg = "等待Chrome浏览器打开超时"
            Logger.error(error_msg)
            raise Exception(error_msg)
        

    def get_location_url(self) -> str:
        """
        获取Chrome浏览器当前页面的URL地址。
        
        Returns:
            str: 当前页面的URL地址，如果获取失败则返回空字符串
        """
        try:
            # 确保Chrome浏览器处于活动状态
            active_window = gw.getActiveWindow()
            if not active_window or 'chrome' not in active_window.title.lower():
                Logger.error("未找到Chrome浏览器窗口")
                return ""
            
            # 使用Ctrl+L选中地址栏
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            
            # 复制地址栏内容
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.3)
            
            # 按Esc取消地址栏选中状态
            pyautogui.press('escape')
            
            root = tk.Tk()
            root.withdraw()  # 不显示窗口
            url = root.clipboard_get()
            root.destroy()
            
            Logger.info(f"获取到当前页面URL: {url}")
            return url
        
        except Exception as e:
            Logger.error(f"获取页面URL失败: {str(e)}", e)
            return ""

    
    def turn_location(self, url: str) -> str:
        """
        chrome 跳转链接
        
        Args:
            url: 需要跳转的目标URL
            
        Returns:
            str: 跳转结果，成功返回目标URL，失败返回空字符串
        """
        try:
            # 确保Chrome浏览器处于活动状态
            active_window = gw.getActiveWindow()
            if not active_window or 'chrome' not in active_window.title.lower():
                # 抛出异常，表示打开设置页面失败
                raise Exception(f"未找到Chrome浏览器窗口")
            
            # 使用Ctrl+L选中地址栏
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            
            # 清空地址栏并输入新URL
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.3)
            pyautogui.write(url)
            time.sleep(0.3)
            
            # 按回车键导航到URL
            pyautogui.press('enter')
            time.sleep(2)  # 等待页面加载
            
            Logger.info(f"已跳转到URL: {url}")
            return url
            
        except Exception as e:
            Logger.error(f"跳转到URL失败: {str(e)}", e)
            return ""


    def login_cursor(self, username: str) -> bool:
        """
        在Cursor登录页面输入用户名和密码并登录
        
        Args:
            username: 用户名/邮箱
            password: 密码
            
        Returns:
            bool: 登录是否成功
        """
        
        # 定位到输入框（通常登录页面的输入框是页面中唯一或第一个输入框）
        # 点击页面中心位置，确保页面获得焦点
        screen_width, screen_height = pyautogui.size()
        pyautogui.click(screen_width // 2, screen_height // 2)
        time.sleep(0.5)
        
        # 检查鼠标是否已经变为光标形状（表示已经在输入框中）
        current_cursor = pyautogui.position()
        cursor_shape = pyautogui.screenshot().getpixel((current_cursor.x, current_cursor.y))
        
        # 如果鼠标不是光标形状（不在输入框中），则使用Tab键定位到输入框
        if cursor_shape != (0, 0, 0):  # 简单判断，实际可能需要更复杂的逻辑
            Logger.info("鼠标未在输入框中，使用Tab键定位")
            pyautogui.press('tab')
            time.sleep(0.3)
        else:
            Logger.info("鼠标已在输入框中，无需再定位")
        
        # 输入用户名
        pyautogui.write(username)
        time.sleep(0.5)
        
        # 按回车键提交表单
        pyautogui.press('enter')
        time.sleep(3)  # 等待登录过程
        
        Logger.info(f"已尝试登录Cursor账号: {username}")
        return True



    def open_setting_page(self) -> bool:
        """判断是否是 Settings 页面"""
        
        currentUrl = self.get_location_url()
        
        # 判断当前URL是否是设置页面或登录页面
        is_settings_page = currentUrl.startswith(CursorConstants.SURSOR_SETTINGS_URL)
        is_sign_page = currentUrl.startswith(CursorConstants.SURSOR_SIGN_URL)
        
        if is_settings_page:
            Logger.info("当前页面是Cursor设置页面")

            return True

        elif is_sign_page:
            Logger.info("当前页面是Cursor登录页面")


        else:
            Logger.warn(f"chrome 打开失败 : Cursor open error .")
            # 抛出异常，表示打开设置页面失败
            raise Exception(f"打开Cursor设置页面失败，当前URL: {currentUrl}")
        return False

        
