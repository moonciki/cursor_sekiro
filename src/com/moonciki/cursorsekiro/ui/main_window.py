"""
主窗口UI模块。
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox, Entry
import os
import time
import json
from typing import Callable, Dict, Any

import pygetwindow as gw
from com.moonciki.cursorsekiro.cursor.chrome_operator import ChromeOperator
from com.moonciki.cursorsekiro.logger import Logger
from com.moonciki.cursorsekiro.cursor.controller import CursorController
from com.moonciki.cursorsekiro.cursor.window import WindowController
from com.moonciki.cursorsekiro.utils.EmailClient import EmailClient
from com.moonciki.cursorsekiro.utils.WindowTools import WindowTools
from com.moonciki.cursorsekiro.utils.constants import CursorConstants
from com.moonciki.cursorsekiro.utils.email_constants import EmailConstants

class MainWindow:
    """
    主窗口类,处理UI相关操作。
    """
    
    def __init__(self, root: tk.Tk):
        """
        初始化主窗口。

        Args:
            root: Tkinter根窗口实例
        """
        self.root = root
        self.root.title("Cursor Sekiro")
        self.root.geometry("600x500")
        
        # 先初始化必要的属性
        self.status_label = None
        self.cursor_controller = None
        self.window_controller = None
        self.chromeOperator = None
        
        # 邮箱相关属性
        self.email_prefix = tk.StringVar()
        self.email_password = tk.StringVar()
        
        # 创建日志组件但不立即显示
        self.log_widget = scrolledtext.ScrolledText(
            self.root,
            height=10,
            font=("Courier", 10),
            state='disabled'
        )
        self.logger = Logger(self.log_widget)
        
        # 加载图标 - 静默处理错误
        try:
            if os.path.exists(CursorConstants.ICON_PATH):
                icon = tk.PhotoImage(file=CursorConstants.ICON_PATH)
                self.root.iconphoto(True, icon)
        except Exception:
            pass
        
        # 加载邮箱配置
        self._load_email_config()
        
        # 设置UI
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """设置用户界面组件。"""
        # 创建上半部分的Frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建邮箱设置区域
        self._create_email_settings(top_frame)
        
        # 创建主标签
        config_status = "邮箱配置已保存" if EmailConstants.is_config_saved() else "邮箱配置未保存"
        status_color = "green" if EmailConstants.is_config_saved() else "red"
        self.main_label = tk.Label(
            top_frame,
            text=config_status,
            font=("Arial", 24),
            fg=status_color
        )
        self.main_label.pack(expand=True, pady=10)
        
        # 添加安全提示
        security_note = tk.Label(
            top_frame,
            text="(注：您的账户与密码均不会上传，但为了安全考虑，请不要使用常用邮箱)",
            font=("Arial", 9),
            fg="red"
        )
        security_note.pack(pady=(0, 5))
        
        # 创建状态标签
        self.status_label = tk.Label(
            top_frame,
            text="点击按钮检查Cursor状态",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        # 创建按钮Frame和按钮
        self._create_buttons(top_frame)
        
        # 创建日志区域
        self._create_log_area()
        
        # 初始化控制器
        self.cursor_controller = CursorController()
        self.window_controller = WindowController()
        self.chromeOperator = ChromeOperator()

    def _create_email_settings(self, parent: tk.Frame) -> None:
        """创建邮箱设置区域"""
        email_frame = tk.Frame(parent)
        email_frame.pack(fill=tk.X, pady=5)
        
        # 邮箱前缀输入框
        email_prefix_frame = tk.Frame(email_frame)
        email_prefix_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            email_prefix_frame,
            text="邮箱:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        email_prefix_entry = Entry(
            email_prefix_frame,
            textvariable=self.email_prefix,
            width=15,
            font=("Arial", 10)
        )
        email_prefix_entry.pack(side=tk.LEFT)
        
        tk.Label(
            email_prefix_frame,
            text="@126.com",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        # 邮箱密码输入框
        password_frame = tk.Frame(email_frame)
        password_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            password_frame,
            text="密码:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        password_entry = Entry(
            password_frame,
            textvariable=self.email_password,
            width=15,
            font=("Arial", 10),
            show="*"
        )
        password_entry.pack(side=tk.LEFT)
        
        # 保存按钮
        self.save_button = tk.Button(
            email_frame,
            text="保存",
            command=self._save_email_config,
            font=("Arial", 10)
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

    def _is_email_saved(self) -> bool:
        """检查是否已保存邮箱配置"""
        return EmailConstants.is_config_saved()

    def _load_email_config(self) -> None:
        """加载邮箱配置"""
        try:
            self.email_prefix.set(EmailConstants.get_email_prefix())
            self.email_password.set(EmailConstants.get_email_password())
            if EmailConstants.is_config_saved():
                Logger.info("邮箱配置已加载")
        except Exception as e:
            Logger.error(f"加载邮箱配置失败: {str(e)}")

    def _save_email_config(self) -> None:
        """保存邮箱配置"""
        try:
            # 保存配置
            EmailConstants.save_config(
                self.email_prefix.get(),
                self.email_password.get()
            )
            
            # 检查保存后的状态
            is_saved = EmailConstants.is_config_saved()
            
            # 根据状态更新主标签
            if is_saved:
                self.main_label.config(text="邮箱配置已保存", fg="green")
                message = "邮箱配置已保存"
            else:
                self.main_label.config(text="邮箱配置未保存", fg="red")
                message = "邮箱配置已保存，但邮箱或密码为空"
            
            messagebox.showinfo("提示", message)
        except Exception as e:
            Logger.error(f"保存邮箱配置失败: {str(e)}")
            messagebox.showerror("错误", f"保存邮箱配置失败: {str(e)}")

    def _create_buttons(self, parent: tk.Frame) -> None:
        """创建按钮区域"""
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=5)
        
        # 检查状态按钮
        tk.Button(
            button_frame,
            text="检查Cursor状态",
            command=self._check_cursor_status,
            font=("Arial", 12)
        ).pack(side=tk.LEFT, padx=5)
        
        # Evil按钮
        tk.Button(
            button_frame,
            text="Evil",
            command=self._launch_cursor,
            font=("Arial", 12),
            fg="red"
        ).pack(side=tk.LEFT, padx=5)
        
        # 登出按钮
        tk.Button(
            button_frame,
            text="退出Cursor登录",
            command=self._logout_cursor,
            font=("Arial", 12),
            fg="blue"
        ).pack(side=tk.LEFT, padx=5)
        
        # 设置按钮
        tk.Button(
            button_frame,
            text="Cursor设置",
            command=self._open_cursor_settings,
            font=("Arial", 12),
            fg="green"
        ).pack(side=tk.LEFT, padx=5)

    def _create_log_area(self) -> None:
        """创建日志区域"""
        log_control_frame = tk.Frame(self.root)
        log_control_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(
            log_control_frame,
            text="操作日志",
            font=("Arial", 12)
        ).pack(side=tk.LEFT, pady=(10, 5))
        
        tk.Button(
            log_control_frame,
            text="清除日志",
            command=self._clear_logs,
            font=("Arial", 10)
        ).pack(side=tk.RIGHT, pady=(10, 5))
        
        # 在这里显示日志组件
        self.log_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        Logger.info("应用程序启动")

    def _check_cursor_status(self) -> None:
        """检查Cursor状态"""
        is_running = self.cursor_controller.is_cursor_running()
        status_text = "Cursor编辑器正在运行" if is_running else "Cursor编辑器未运行"
        self.status_label.config(text=status_text)
        Logger.info(f"检查Cursor状态: {status_text}")

        Logger.info("测试开始");
    
        search_region = (
            0,0,
            1920,
            1080
        )

        WindowTools.capture_region_image(search_region)

        email_client = EmailClient()
        if email_client.connect():
            latest_emails = email_client.get_latest_emails(limit=10)
            for email in latest_emails:
                print(f"主题: {email['subject']}")
                print(f"发件人: {email['from']}")
                print(f"日期: {email['date']}")
                print(f"内容: {email['body'][:100]}...")  # 只显示前100个字符
                print("-" * 50)
            email_client.disconnect()

        Logger.info(f"clieck_result ")


    def _launch_cursor(self) -> None:
        """启动Cursor"""
        self.cursor_controller.launch_cursor()

    def _logout_cursor(self) -> None:
        """退出Cursor登录"""
        try:
            # 先尝试通过UI点击登出
            if self.window_controller.click_logout_button():
                time.sleep(1)  # 等待登出操作完成
            
            # 无论UI操作是否成功,都执行强制登出
            #self.cursor_controller.logout_cursor()
            
        except Exception as e:
            Logger.error(f"登出操作失败: {str(e)}")

    def _clear_logs(self) -> None:
        """清除日志"""
        Logger.clear()

    def _open_cursor_settings(self) -> None:
        """打开Cursor设置"""
        try:
            # 首先检查 Cursor.exe 是否存在
            if not os.path.exists(CursorConstants.CURSOR_EXE_PATH):
                error_msg = f"未找到Cursor程序，请确认Cursor已正确安装。\n期望路径: {CursorConstants.CURSOR_EXE_PATH}"
                Logger.error(error_msg)
                messagebox.showerror("错误", error_msg)
                return
                
            result = messagebox.showwarning(
                "操作提示",
                "激活过程中，请勿操作电脑",
                icon='warning'
            )
            
            if result == 'ok':
                Logger.info("开始打开Cursor设置流程")
                
                if not self.cursor_controller.is_cursor_running():
                    Logger.info("Cursor未运行，正在启动...")
                    self.cursor_controller.launch_cursor()

                    # 循环检查Cursor是否运行,最多等待30秒
                    wait_time = 0
                    while not self.cursor_controller.is_cursor_running():
                        time.sleep(3)
                        wait_time += 1
                        Logger.info(f"等待Cursor启动... {wait_time}秒")
                        if wait_time >= 30:
                            error_msg = "等待Cursor启动超时"
                            Logger.error(error_msg)
                            messagebox.showerror("错误", error_msg)
                            return
                    Logger.info("等待 Cursor 启动 。。。 ")
                    time.sleep(10)
                    Logger.info("Cursor已成功启动 ！")

                else:
                    Logger.info("Cursor已运行 ...")
                
                self.window_controller.focus_cursor_window()
                time.sleep(1)
                
                self.window_controller.click_cursor_setting()
                time.sleep(1)
                
                manaResult = self.window_controller.click_cursor_manager()

                if(not manaResult):
                    Logger.warn("当前账号未登录")

                    #点击 sign
                    signResult = self.window_controller.click_cursor_sign()

                    time.sleep(4)
                    if (not signResult):
                        Logger.warn("打开浏览器失败...")
                        return;

                else:
                    Logger.info("Manage 成功")
                
                Logger.info("正在打开浏览器...")
                time.sleep(1)

                #循环判断是否有chrome 
                self.chromeOperator.check_chrome_open()
                
                Logger.info("chrome 浏览器打开完毕...")
                time.sleep(1)

                self.chromeOperator.loop_check_setting()

                time.sleep(1)
                
                # 删除账号
                self.chromeOperator.delete_cursor_account()
                time.sleep(1)

                # 登录
                self.chromeOperator.do_cursor_login()
                time.sleep(1)



                
        except Exception as e:
            Logger.error("打开设置失败: ", e)
            
             