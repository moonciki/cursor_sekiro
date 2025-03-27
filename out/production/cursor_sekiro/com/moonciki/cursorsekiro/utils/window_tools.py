"""
Cursor控制器模块,处理Cursor编辑器的核心操作。
"""
import os
import time
import pyautogui
import pyperclip
from pyscreeze import Box
import win32com.client
from typing import Optional, Tuple
from ..logger import Logger
from .cursor_constants import CursorConstants
import win32process
import pythoncom
import numpy as np
import cv2

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
    def focus_window_by_process(process_name):
        pythoncom.CoInitialize()
        wmi = win32com.client.GetObject("winmgmts:")
        processes = wmi.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{process_name}'")
        # 只获取第一个进程的PID
        for process in processes:
            onePid = process.Properties_("ProcessID").Value

            focusResult = WindowTools.focus_pid_window(onePid)
            if focusResult:
                return True

        return False

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
                        time.sleep(1)
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
            # 使用OpenCV查找按钮位置
            button_location = WindowTools._find_img_position(button_image_name, search_region)
            
            if button_location:
                # 获取当前活动窗口
                window = gw.getActiveWindow()
                
                # 计算按钮中心点
                button_center_x = button_location.left + button_location.width // 2
                button_center_y = button_location.top + button_location.height // 2
                
                # 确保按钮在当前窗口内
                if (window.left <= button_center_x <= window.right and 
                    window.top <= button_center_y <= window.bottom):
                    # 移动到按钮中心并点击
                    pyautogui.moveTo(button_center_x, button_center_y)
                    pyautogui.click()
                    Logger.info(f"成功点击按钮: {button_image_name}")
                    return True
                else:
                    Logger.warn(f"按钮 {button_image_name} 不在当前窗口内")
            
            Logger.info(f"未找到按钮: {button_image_name}")
            return False
            
        except Exception as e:
            Logger.error(f"点击按钮失败: {str(e)}")
            return False



    @staticmethod
    def _find_img_position(image_name: str, search_region: Tuple[int, int, int, int]) -> Optional[Box]:
        """
        使用OpenCV在屏幕上查找指定图片的位置。
        
        Args:
            image_name: 图片文件名
            search_region: 搜索区域的坐标 (left, top, width, height)
        
        Returns:
            Optional[Box]: 找到的图片位置，未找到则返回None
        """
        button_image_path = os.path.join(CursorConstants.RESOURCES_DIR, image_name)
        
        if not os.path.exists(button_image_path):
            Logger.error(f"图片不存在: {button_image_path}")
            raise Exception(f"图片不存在: {button_image_path}")
           
        try:
            # 截取屏幕区域
            left, top, width, height = search_region
            screenshot = pyautogui.screenshot(region=search_region)
            screenshot_np = np.array(screenshot)
            
            # 读取模板图像
            template = cv2.imread(button_image_path)
            template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
            
            # 获取模板尺寸
            h, w = template.shape[:2]
            
            # 执行模板匹配
            result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 如果匹配度高于阈值
            if max_val > 0.8:
                # 转换为屏幕坐标
                screen_x = left + max_loc[0]
                screen_y = top + max_loc[1]
                return Box(left=screen_x, top=screen_y, width=w, height=h)
            
            return None
            
        except Exception as e:
            Logger.error(f"查找图片失败: ", e)
            raise e

    @staticmethod
    def loop_check_img_exist(search_region: Tuple[int, int, int, int], *button_images: str) -> bool:
        """
        找图
        """
        
        for image in button_images:
            button_location = WindowTools._find_img_position(image, search_region)
            if button_location:
                return True
        return False
    
    @staticmethod
    def loop_find_img_position(search_region: Tuple[int, int, int, int], *button_images: str) -> Optional[Box]:
        """
        在指定区域内查找多个图片中的任意一个，返回找到的第一个图片位置
        
        Args:
            search_region: 搜索区域的坐标 (left, top, width, height)
            button_images: 要查找的图片文件名列表
            
        Returns:
            Optional[Box]: 找到的图片位置，未找到则返回None
        """
        
        for image in button_images:
            button_location = WindowTools._find_img_position(image, search_region)

            if button_location:
                return button_location
        return None
    
    @staticmethod
    def mouse_move_to(x: int, y: int, duration: float = 0.2) -> None:
        """
        鼠标移动到指定坐标
        
        Args:
            x: 目标x坐标
            y: 目标y坐标
            duration: 移动持续时间，默认0.2秒
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            Logger.info(f"鼠标已移动到坐标: ({x}, {y})")
        except Exception as e:
            Logger.error(f"鼠标移动失败: {e}")
            raise e
    
    @staticmethod
    def mouse_left_down() -> None:
        """
        鼠标左键按下
        """
        try:
            pyautogui.mouseDown(button='left')
            Logger.info("鼠标左键已按下")
        except Exception as e:
            Logger.error(f"鼠标左键按下失败: {e}")
            raise e

    @staticmethod
    def mouse_left_up() -> None:
        """
        鼠标左键抬起
        """
        try:
            pyautogui.mouseUp(button='left')
            Logger.info("鼠标左键已抬起")
        except Exception as e:
            Logger.error(f"鼠标左键抬起失败: {e}")
            raise e


    @staticmethod
    def mouse_select_text(from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 0.2) -> None:
        """
        鼠标选择文本
        
        Args:
            from_x: 起始点x坐标
            from_y: 起始点y坐标
            to_x: 结束点x坐标
            to_y: 结束点y坐标
            duration: 移动持续时间，默认0.2秒
        """
        try:
            # 移动到起始位置
            WindowTools.mouse_move_to(from_x, from_y, duration)
            # 按下鼠标左键
            WindowTools.mouse_left_down()
            time.sleep(duration)
            # 移动到结束位置
            WindowTools.mouse_move_to(to_x, to_y, duration)
            time.sleep(duration)
            # 释放鼠标左键
            WindowTools.mouse_left_up()
            Logger.info(f"已选择从 ({from_x}, {from_y}) 到 ({to_x}, {to_y}) 的文本")
        except Exception as e:
            Logger.error(f"文本选择失败: {e}")
            raise e
        
