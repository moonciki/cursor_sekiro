"""
Cursor控制器模块,处理Cursor编辑器的核心操作。
"""
import os
import time
from typing import List
import psutil
import pygetwindow as gw

from ..utils.window_tools import WindowTools
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
        try:
            CursorController.focus_cursor_window()
            Logger.info("Cursor 已启动 ... ")
            return True
        except Exception as e:
            Logger.info("Cursor 未启动 ...")
            return False

    @staticmethod
    def run_cursor(always : bool = False) -> bool:
        """
        查询 Cursor.exe 进程是否存在。
        """
        if (not always and CursorController.is_cursor_running()):
            Logger.info("Cursor已运行")
            return

        Logger.info("#####Cursor未运行，正在启动...")
        CursorController.launch_cursor()
        time.sleep(0.5)


    @staticmethod
    def launch_cursor() -> None:
        """启动Cursor编辑器。"""
        try:
            os.startfile(CursorConstants.CURSOR_EXE_PATH)
            Logger.info("正在启动Cursor")
            time.sleep(1)

            wait_time = 0
            while wait_time < 15:

                try:
                    CursorController.focus_cursor_window()
                    window = CursorController.get_cursor_window()

                    # 设置按钮通常在右上角
                    search_region = (
                        max(0, window.right - 800),
                        max(0, window.top),
                        min(800, window.right),
                        min(300, window.height)
                    )
                    # 是否有settings按钮
                    result_settings = WindowTools.loop_check_img_exist(search_region, *CursorConstants.SETTING_BUTTON_IMAGES)

                    if result_settings:
                        Logger.info("Cursor 启动成功 ... ")
                        break;

                except Exception as e:
                    Logger.warn(f"Cursor 启动中，请稍候 ... {wait_time}秒")

                wait_time += 1
                Logger.info(f"等待Cursor 启动 ... {wait_time}秒")
                time.sleep(1)
            else:
                error_msg = "Cursor 启动超时"
                Logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            Logger.error(f"启动Cursor失败: {str(e)}")
            raise e


    @staticmethod
    def focus_cursor_window():
        """聚焦Cursor窗口。"""
        result = WindowTools.focus_window_by_process(CursorConstants.CURSOR_PROCESS_NAME)

        if not result:
            Logger.error("无法聚焦Cursor窗口")
            raise Exception("无法聚焦Cursor窗口")
        
        # 检查窗口是否已经最大化，如果没有则最大化
        active_window = gw.getActiveWindow()
        if not active_window.isMaximized:
            active_window.maximize()
            Logger.info("Cursor窗口最大化")

        else:
            Logger.info("Cursor窗口已经处于最大化状态")



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
    def check_cursor_login() -> bool:

        time.sleep(0.5)

        window = CursorController.get_cursor_window()
            
        time.sleep(0.5)
        # 登出按钮通常在整个窗口范围内
        search_region = (
            0,
            0, 
            max(0, window.width),
            max(0, window.height)
        )
        # 是否有登录按钮
        result_sign = WindowTools.loop_check_img_exist(search_region, *CursorConstants.SIGN_BUTTON_IMAGES)
        time.sleep(0.5)
        # 是否有登出按钮
        result_loginout = WindowTools.loop_check_img_exist(search_region, *CursorConstants.MANAGE_BUTTON_IMAGES)

        if(result_loginout):
            return True

        if(result_sign):
            return False

        return False

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
        
        result = WindowTools.loop_click_button_once(search_region, *CursorConstants.LOGOUT_BUTTON_IMAGES)

        if not result:
            Logger.error("无法点击Cursor登出按钮")
            raise Exception("无法点击Cursor登出按钮")









    @staticmethod
    def get_cursor_processes() -> List[psutil.Process]:
        """
        获取所有运行中的Cursor相关进程

        Returns:
            List[psutil.Process]: Cursor相关进程列表
        """
        cursor_processes = []
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] in CursorConstants.CURSOR_PROCESS_NAMES:
                    cursor_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return cursor_processes

    @staticmethod
    def terminate_process(process: psutil.Process) -> bool:
        """
        尝试终止单个进程

        Args:
            process: 要终止的进程

        Returns:
            bool: 是否成功终止进程
        """
        try:
            process_name = process.name()
            pid = process.pid
            
            # 首先尝试正常终止
            process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=3)
                Logger.info(f"终止进程: {process_name} (PID: {pid})")
                return True
            except psutil.TimeoutExpired:
                # 如果超时，强制结束进程
                process.kill()
                Logger.warn(f"强制终止: {process_name} (PID: {pid})")
                return True
                
        except psutil.NoSuchProcess:
            Logger.info(f"进程不存在: {process_name} (PID: {pid})")
            return True
        except Exception as e:
            Logger.error(f"终止失败: {str(e)}", e)
            return False

    @staticmethod
    def close_cursor() -> bool:
        """
        关闭所有Cursor相关进程

        Returns:
            bool: 是否成功关闭所有进程
        """
        cursor_processes = CursorController.get_cursor_processes()
        
        if not cursor_processes:
            Logger.info("未发现Cursor进程")
            return True
            
        success = True
        for process in cursor_processes:
            if not CursorController.terminate_process(process):
                success = False
                
        # 最后验证
        remaining_processes = CursorController.get_cursor_processes()
        if remaining_processes:
            process_list = ", ".join([f"{p.name()} (PID: {p.pid})" for p in remaining_processes])
            Logger.error(f"未能关闭的进程: {process_list}")
            return False

        Logger.info("所有Cursor进程已关闭")
        return success


