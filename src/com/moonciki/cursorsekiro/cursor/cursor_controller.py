"""
Cursor控制器模块,处理Cursor编辑器的核心操作。
"""
import os
import subprocess
import time
import psutil
import win32com.client
import shutil
import pygetwindow as gw
from typing import Optional
from  ..utils.window_tools import WindowTools
from ..logger import Logger
from ..utils.cursor_constants import CursorConstants

class CursorController:
    """
    Cursor控制器类。
    """

    @staticmethod
    def is_cursor_running() -> bool:
        """
        查询 Cursor.exe 进程是否存在。
        """
        runResult = WindowTools.is_process_running(CursorConstants.CURSOR_PROCESS_NAME)
        return runResult


    @staticmethod
    def run_cursor() -> bool:
        """
        查询 Cursor.exe 进程是否存在。
        """
        if CursorController.is_cursor_running():
            Logger.info("Cursor已运行")
            return

        Logger.info("Cursor未运行，正在启动...")
        CursorController.launch_cursor()
        
        wait_time = 0
        while wait_time < 15:
            if CursorController.is_cursor_running():
                return True

            time.sleep(1)
            wait_time += 1
            Logger.info(f"等待Cursor启动... {wait_time}/15")
        else:
            Logger.error("等待Cursor启动超时")
            raise Exception("等待Cursor启动超时")
        

    @staticmethod
    def launch_cursor() -> None:
        """启动Cursor编辑器。"""
        try:
            if not CursorController.is_cursor_running():
                os.startfile(CursorConstants.CURSOR_EXE_PATH)
                Logger.info("已启动Cursor")
            else:
                Logger.info("Cursor已在运行")
        except Exception as e:
            Logger.error(f"启动Cursor失败: {str(e)}")
            raise e


    @staticmethod
    def focus_cursor_window():
        """聚焦Cursor窗口。"""
        pid = WindowTools.get_pid_by_process_name(CursorConstants.CURSOR_PROCESS_NAME)

        # 判断是否找到 Cursor 进程
        if not pid:
            Logger.error("未找到 Cursor 进程")
            raise Exception("未找到 Cursor 进程")
        
        Logger.info(f"找到 Cursor 进程，PID: {pid}")
        result = WindowTools.focus_pid_window(pid)

        if not result:
            Logger.error("无法聚焦Cursor窗口")
            raise Exception("无法聚焦Cursor窗口")


    @staticmethod
    def logout_cursor() -> None:
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
            
            Logger.info("已退出Cursor登录")
        except Exception as e:
            Logger.error(f"退出Cursor登录失败: {str(e)}") 


    @staticmethod
    def get_cursor_window():
        """
        检查并获取当前活动的Cursor窗口。
        
        Returns:
            pygetwindow.Window: Cursor窗口对象
            
        Raises:
            Exception: 当前活动窗口不是Cursor时抛出异常
        """
        window = gw.getActiveWindow()
        if not window:
            Logger.warn("未能获取当前活动窗口")
            raise Exception("未能获取当前活动窗口")
            
        if 'cursor' not in window.title.lower():
            Logger.warn("当前窗口不是Cursor，窗口标题：" + window.title)
            raise Exception("当前窗口不是Cursor")

        return window


    @staticmethod
    def click_cursor_setting():
        """点击Cursor设置按钮"""
        window = CursorController.get_cursor_window()
        
        # 设置按钮通常在右上角
        search_region = (
            max(0, window.right - 800),
            max(0, window.top),
            min(800, window.right),
            min(300, window.height)
        )
        result = WindowTools.loop_click_button_once(search_region, *CursorConstants.SETTING_BUTTON_IMAGES)

        if not result:
            Logger.error("无法点击Cursor设置按钮")
            raise Exception("无法点击Cursor设置按钮")
        

    @staticmethod
    def click_cursor_manager() -> bool:
        """点击Cursor manager按钮"""
        window = CursorController.get_cursor_window()
            
        # 登出按钮通常在整个窗口范围内
        search_region = (
            max(0, window.left),
            max(0, window.top), 
            max(0, window.width),
            max(0, window.height)
        )

        result = WindowTools.loop_click_button_once(search_region, *CursorConstants.MANAGE_BUTTON_IMAGES)
        return result

    @staticmethod
    def click_cursor_sign():
        """点击Cursor sign按钮"""
        window = CursorController.get_cursor_window()
            
        # 登出按钮通常在整个窗口范围内
        search_region = (
            max(0, window.left),
            max(0, window.top), 
            max(0, window.width),
            max(0, window.height)
        )
        
        result = WindowTools.loop_click_button_once(search_region, *CursorConstants.SIGN_BUTTON_IMAGES)

        if not result:
            Logger.error("无法点击Cursor sign按钮")
            raise Exception("无法点击Cursor sign按钮")

    @staticmethod
    def click_cursor_logout():
        """点击Cursor登出按钮"""
        window = CursorController.get_cursor_window()
            
        # 登出按钮通常在整个窗口范围内
        search_region = (
            max(0, window.left),
            max(0, window.top), 
            max(0, window.width),
            max(0, window.height)
        )
        
        WindowTools.capture_region_image(search_region)

        result = WindowTools.loop_click_button_once(search_region, *CursorConstants.LOGOUT_BUTTON_IMAGES)

        if not result:
            Logger.error("无法点击Cursor登出按钮")
            raise Exception("无法点击Cursor登出按钮")

