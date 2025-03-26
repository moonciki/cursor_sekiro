"""
窗口操作模块,处理Cursor窗口的操作。
"""
import time
import psutil
import pyperclip
import win32com.client
import win32gui
import win32process
import win32con
import pyautogui
import pygetwindow as gw
import os
from typing import Optional, Tuple

from com.moonciki.cursorsekiro.utils.email_constants import EmailConstants
from ..logger import Logger
from ..utils.constants import CursorConstants
from ..utils.WindowTools import WindowTools

from tkinter import messagebox
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

            current_title = active_window.title.lower()

            Logger.info(f"windows title : {current_title}")

            if active_window and 'google chrome' in current_title:
                Logger.info("Chrome浏览器已打开")

                # 检查窗口是否已经最大化，如果没有则最大化
                if not active_window.isMaximized:
                    active_window.maximize()
                    Logger.info("Chrome浏览器已最大化")

                    #按 ctrl + 0 恢复缩放等级
                    pyautogui.hotkey('ctrl', '0')
                    Logger.info("已恢复Chrome浏览器默认缩放等级")

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
            if not active_window or 'google chrome' not in active_window.title.lower():
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
            WindowTools.paste_text(url)
            time.sleep(0.3)
            
            # 按回车键导航到URL
            pyautogui.press('enter')
            time.sleep(2)  # 等待页面加载
            
            Logger.info(f"已跳转到URL: {url}")
            return url
            
        except Exception as e:
            Logger.error(f"跳转到URL失败: {str(e)}", e)
            return ""


    def send_login_code(self) -> bool:
        """
        发送登录验证码
        """
        
        window = gw.getActiveWindow()
        search_region = (
            max(0, window.left),
            max(0, window.top),
            window.width,
            window.height
        )

        clickResult = WindowTools.loop_click_button_multi(
            search_region, 
            *CursorConstants.CHROME_BTN_EMAIL_CODE_IMAGE, 
            tryCount=5
        )
        
        if(not clickResult):
            Logger.warn("登录按钮点击失败")
            raise Exception("登录按钮点击失败")

        Logger.info("发送登录验证码点击成功")

        # 定位到输入框（通常登录页面的输入框是页面中唯一或第一个输入框）
        window = gw.getActiveWindow()
        
        
        wait_time = 0
        while wait_time < 5:

            clickResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_BTN_ROBOT_CHECK_IMAGE)

            if(not clickResult):
                Logger.warn("机器人校验没看到")

                clickResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_PAGE_ENTER_CODE)
        
                if(not clickResult):
                    Logger.warn("也不是输入验证码页面")
                else:
                    time.sleep(0.5)
                    pyautogui.press('tab')
                    Logger.info("输入验证码页面")
                    break
            
            wait_time += 1
            Logger.info(f"尝试发送登录验证码 ... {wait_time}秒")
            time.sleep(2)
        else:
            error_msg = "尝试发送登录验证码超时"
            Logger.error(error_msg)
            raise Exception(error_msg)


    def receive_email(self) -> bool:
        """
        接收邮件
        """
        
        window = gw.getActiveWindow()

        search_region = (
            max(0, window.left),
            max(0, window.top),
            window.width,
            window.height
        )

        wait_time = 0
        while wait_time < 5:
            # 点击ctrl + f 输入框
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)

            WindowTools.paste_text("收 信")

            clickResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_BTN_RECEIVE_EMAIL)

            if(clickResult):
                return True

            else:
                wait_time += 1
                Logger.info(f"等待 收信 ... {wait_time}秒")
                time.sleep(2)
        else:
            error_msg = "收信点击失败"
            Logger.error(error_msg)
            raise Exception(error_msg)


    def click_new_email(self) -> bool:
        """
        点击新邮件
        """
        
        window = gw.getActiveWindow()

        search_region = (
            max(0, window.left),
            max(0, window.top),
            min(window.width, 1000),
            min(window.height, 600)
        )

        wait_time = 0
        while wait_time < 2:
            # 点击ctrl + f 输入框
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)


            Logger.info("检查是否收到 Cursor 新邮件")

            clickResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_BTN_NEW_EMAIL)

            if(clickResult):
                Logger.info("已收到 Cursor 新邮件")
                return True

            else:
                wait_time += 1
                Logger.info(f"查询新邮件 ... {wait_time}秒")
                time.sleep(2)
        else:
            return False

    def get_email_code(self) -> str:
        """
        获取邮件内容
        """

        window = gw.getActiveWindow()

        search_region = (
            max(0, window.left),
            max(0, window.top),
            window.width,
            window.height
        )

        wait_time = 0
        clickResult = False
        while wait_time < 5:
            clickResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_EMAIL_CONTENT)
            if clickResult:
                Logger.info("成功点击邮件内容")
                break
            else:
                wait_time += 1
                Logger.info(f"尝试点击邮件内容 ... 第{wait_time}次")
                time.sleep(1)
        else:
            error_msg = "邮件内容获取失败"
            Logger.error(error_msg)
            raise Exception(error_msg)


        # ctrl + a 全选
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)

        # ctrl + c 复制
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)

        # 获取剪贴板内容    
        email_content = pyperclip.paste()

        Logger.info(f"邮件内容: {email_content}")

        # 截取字符串
        # Your one-time code is:   与  This code expires in 中间的字符串

        front_text = "Your one-time code is:"
        end_text = "This code expires in"

        start_index = email_content.find(front_text) + len(front_text)
        end_index = email_content.find(end_text)
        code = email_content[start_index:end_index].strip()
        code = code.strip()
        Logger.info(f"验证码: {code}")
        return code

    def all_read_email(self):
        """
        全部阅读邮件
        """

        window = gw.getActiveWindow()   

        time.sleep(1)

        search_region = (
            max(0, window.left),
            max(0, window.top),
            window.width,
            window.height
        )

        receive_email_result = self.receive_email()

        if(not receive_email_result):
            Logger.warn("收信失败")
            raise Exception("收信失败")


        # 点击ctrl + f 输入框
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)

        WindowTools.paste_text("全部设为已读")
        time.sleep(0.5)

        clickResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_BTN_ALL_READ)

        if(not clickResult):
            Logger.warn("全部阅读失败")


    def email_login(self) -> str:
        """
        邮箱登录
        """

        # 按 ctrl + N 打开新窗口
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(2)
        
        self.turn_location(CursorConstants.EMAIL_126_URL)
        time.sleep(1)

        wait_time = 0
        while wait_time < 20:

            self.receive_email()
            time.sleep(1)

            clickResult = self.click_new_email()

            if(clickResult):
                break;

            else:
                wait_time += 1
                Logger.info(f"查询新邮件 ... {wait_time}秒")
                time.sleep(2)

        else:
            error_msg = "查询新邮件超时"
            Logger.error(error_msg)
            raise Exception(error_msg)

        # 获取邮件内容
        email_code = self.get_email_code()

        self.all_read_email()

        # 按 ctrl + w 关闭新窗口
        pyautogui.hotkey('ctrl', 'w')

        return email_code


    def login_cursor(self) -> bool:
        """
        在Cursor登录页面输入用户名和密码并登录
        
        Args:
            username: 用户名/邮箱
            password: 密码
            
        Returns:
            bool: 登录是否成功
        """
        
        # 定位到输入框（通常登录页面的输入框是页面中唯一或第一个输入框）
        window = gw.getActiveWindow()

        search_region = (
            max(0, window.left),
            max(0, window.top),
            window.width,
            window.height
        )
        
        clickResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_SIGN_BLUR_IMAGES)
        if(not clickResult):
            raise Exception("登录页面解析失败!")

        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.3)
        
        # 输入用户名
        email = EmailConstants.get_email()
        if email:
            WindowTools.paste_text(email)
        else:
            # 如果没有配置邮箱，则抛出异常并弹出提示
            error_msg = "未配置邮箱信息，请先在设置中配置邮箱"
            Logger.error(error_msg)
            messagebox.showerror("错误", error_msg)
            raise Exception("未配置邮箱信息")
        
        time.sleep(0.5)
        
        # 按回车键提交表单
        pyautogui.press('enter')
        time.sleep(3)  # 等待登录过程
    
        #发送登录验证码
        self.send_login_code()

        # 登录邮箱内查看
        cursorCode = self.email_login()

        # 输入验证码
        clickResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_SIGN_BLUR_IMAGES)
        if(not clickResult):
            raise Exception("验证码页面解析失败!")

        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.3)

        WindowTools.paste_text(cursorCode)
        time.sleep(2)
        Logger.info("输入验证码成功，正在登录 ... ")


        

        #########################

        Logger.info(f"已尝试登录Cursor账号")
        return True



    def _cursor_setting_page(self) -> bool:
        """判断是否是 Settings 页面"""
        
        currentUrl = self.get_location_url()
        
        

        is_setting_page = currentUrl.startswith(CursorConstants.SURSOR_SETTINGS_URL)
        is_sign_page = currentUrl.startswith(CursorConstants.SURSOR_SIGN_URL)
        
        if is_setting_page:
            Logger.info("当前页面是Cursor设置页面")


            Logger.info("检查settings 页面加载 。。。 ")
            window = gw.getActiveWindow()
            # 判断当前URL是否是设置页面或登录页面
            search_region = (
                max(0, window.left),
                max(0, window.top), 
                max(0, window.width),
                max(0, window.height)
            )
            settingResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_SETTING_PAGE_IMG)

            return settingResult

        elif is_sign_page:
            Logger.info("当前页面是Cursor登录页面")
            self.login_cursor()

            return False
        else:
            Logger.warn(f"既不是登录，也不是 Settings .")
            self.turn_location(CursorConstants.SURSOR_SETTINGS_URL)
            return False


    def do_cursor_login(self) -> bool:
        """判断是否是 login 页面"""
        
        currentUrl = self.get_location_url()
        
        # 判断当前URL是否是登录页面
        is_sign_page = currentUrl.startswith(CursorConstants.SURSOR_SIGN_URL)
        
        if not is_sign_page:

            self.turn_location(CursorConstants.SURSOR_SIGN_URL)

            time.sleep(2)

        self.login_cursor()
        return True

    def delete_cursor_account(self):
        """删除Cursor账号"""

        window = gw.getActiveWindow()
         
        # 登出按钮通常在整个窗口范围内
        search_region = (
            max(0, window.left),
            max(0, window.top), 
            max(0, window.width),
            max(0, window.height)
        )
        
        btnAdvanceDelete = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_ADVANCE_DELETE_IMAGE)

        if(not btnAdvanceDelete):
            btnAdvanceDelete = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_ADVANCE_IMAGE)

            if(not btnAdvanceDelete):
                Logger.warn("高级按钮点击失败")
                raise Exception("高级按钮点击失败")

            time.sleep(0.5)
            
            btnAdvanceDelete = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_ADVANCE_DELETE_IMAGE)

            if(not btnAdvanceDelete):
                Logger.warn("删除按钮点击失败")
                raise Exception("删除账号失败")

        time.sleep(0.5)
        
        inputResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_INPUT_CONFIRM_IMAGE)

        if(not inputResult):
            Logger.warn("确认输入框点击失败")
            raise Exception("确认输入框点击失败")

        WindowTools.paste_text("delete")
        time.sleep(0.3)
        deleteResult = WindowTools.loop_click_button_once(search_region, *CursorConstants.CHROME_BTN_DELETE_CONFIRM)

        if(not deleteResult):
            Logger.warn("账号确认删除失败")
            raise Exception("账号确认删除失败")

        time.sleep(2)
        
        Logger.info("账号删除成功")












    def loop_check_setting(self):
        wait_time = 0
        while wait_time < 5:

            openSult = self._cursor_setting_page()

            # 检查窗口是否已经最大化，如果没有则最大化
            if openSult:
                Logger.info("Cursor 设置页面打开成功 ... ")
                break;
            else:
                wait_time += 1
                Logger.info(f"等待Cursor setting page ... {wait_time}秒")
                time.sleep(2)
        else:
            error_msg = "Cursor setting page打开超时"
            Logger.error(error_msg)
            raise Exception(error_msg)
    
    