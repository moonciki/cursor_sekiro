"""
主窗口UI模块。
"""
import os
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox, Entry, Toplevel, Label

from com.moonciki.cursorsekiro.cursor.chrome_operator import ChromeOperator
from com.moonciki.cursorsekiro.cursor.cursor_controller import CursorController
from com.moonciki.cursorsekiro.cursor.cursor_reset import CursorReset
from com.moonciki.cursorsekiro.logger import Logger
from com.moonciki.cursorsekiro.utils.cursor_constants import CursorConstants
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
        self.chromeOperator = None
        
        # 邮箱相关属性
        self.email_prefix = tk.StringVar()
        self.disable_auto_update = tk.BooleanVar(value=True)
        
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
                self.root.iconbitmap(CursorConstants.ICON_PATH)
        except Exception:
            pass
        
        # 加载邮箱配置
        self._load_email_config()

        # 设置UI
        self._setup_ui()
        
        # 添加任务控制标志
        self.task_running = False
        self.warning_window = None
        
        # 注册热键
        self._register_hotkey()
        
        # 设置窗口关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _register_hotkey(self):
        """注册热键"""
        try:
            # 注册 Ctrl+Q 热键
            self.root.bind('<Control-q>', self._on_hotkey_activated)
            Logger.info("热键 Ctrl+Q 已注册")
        except Exception as e:
            Logger.error("注册热键异常:", e)
    
    def _on_hotkey_activated(self, event=None):
        """热键激活时的回调"""
        print("@@@@@@@@@@@")  # 添加这行打印信息
        self._handle_interrupt()
    
    def _on_closing(self):
        """窗口关闭时的处理"""
        self.root.destroy()
        
    def _setup_ui(self) -> None:
        """设置用户界面组件。"""
        # 创建上半部分的Frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建邮箱设置区域
        self._create_email_settings(top_frame)
        
        # 添加运行前提提示 - 使用Text控件替代Label以支持文本选择
        prerequisites_text = tk.Text(
            top_frame,
            height=6,
            width=200,
            font=("Arial", 10),
            fg="blue",
            wrap=tk.WORD,
            borderwidth=0,
            highlightthickness=0,
            background=top_frame.cget("background")
        )
        prerequisites_text.insert("1.0", 
            "运行前提：\n"
            "1. 运行之前，请确保所有文件已保存\n"
            "2. 确保系统默认浏览器是 Chrome\n"
            "3. 确保系统显示无缩放，无变色\n"
            "4. 本工具目前只支持126邮箱，运行前，请在chrome 中登录，并勾选30 天免登录\n"
            "5. 微信公众号：曼哈顿阿童木\n"
        )
        prerequisites_text.configure(state="disabled")  # 设为只读，但仍可选择
        prerequisites_text.pack(pady=10)
        
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
        self.chromeOperator = ChromeOperator()

    def _create_email_settings(self, parent: tk.Frame) -> None:
        """创建邮箱设置区域"""
        email_frame = tk.Frame(parent)
        email_frame.pack(fill=tk.X, pady=5)

        # 禁用自动更新选项
        disable_update_cb = tk.Checkbutton(
            email_frame,
            text="禁用自动更新",
            variable=self.disable_auto_update,
            font=("Arial", 10)
        )
        disable_update_cb.pack(side=tk.LEFT, padx=(5, 10))

        # 邮箱标签
        tk.Label(
            email_frame,
            text="邮箱:",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        # 邮箱前缀输入框
        email_prefix_entry = Entry(
            email_frame,
            textvariable=self.email_prefix,
            width=15,
            font=("Arial", 10)
        )
        email_prefix_entry.pack(side=tk.LEFT)

        # 邮箱后缀
        tk.Label(
            email_frame,
            text="@126.com",
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        # 保存按钮
        self.save_button = tk.Button(
            email_frame,
            text="保存",
            command=self._save_email_config,
            font=("Arial", 10)
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        # 配置状态标签
        try:
            email_prefix = EmailConstants.get_email_prefix()
            config_status = "(邮箱配置已保存)" if email_prefix and email_prefix.strip() else "(请配置邮箱)"
            status_color = "green" if email_prefix and email_prefix.strip() else "red"
        except Exception:
            config_status = "(请配置邮箱)"
            status_color = "red"
            
        self.config_status_label = tk.Label(
            email_frame,
            text=config_status,
            font=("Arial", 10),
            fg=status_color
        )
        self.config_status_label.pack(side=tk.LEFT)

    def _is_email_saved(self) -> bool:
        """检查是否已保存邮箱配置"""
        return EmailConstants.is_config_saved()

    def _load_email_config(self) -> None:
        """加载邮箱配置"""
        try:
            self.email_prefix.set(EmailConstants.get_email_prefix())
            self.disable_auto_update.set(EmailConstants.get_disable_auto_update())
            if EmailConstants.is_config_saved():
                Logger.info("邮箱配置已加载")
        except Exception as e:
            Logger.info("首次使用，请配置邮箱")

    def _save_email_config(self) -> None:
        """保存邮箱配置"""
        try:
            email_prefix = self.email_prefix.get().strip()
            
            # 检查邮箱前缀是否为空
            if not email_prefix:
                self.config_status_label.config(text="(请配置邮箱)", fg="red")
                messagebox.showwarning("提示", "请输入邮箱前缀")
                return
                
            # 保存配置，包含自动更新设置
            EmailConstants.save_config(
                email_prefix, 
                "",
                self.disable_auto_update.get()
            )
            
            # 更新UI状态
            self.config_status_label.config(text="(邮箱配置已保存)", fg="green")
            Logger.info(f"邮箱配置已保存: {email_prefix}@126.com")
            messagebox.showinfo("提示", "邮箱配置已保存")
            
        except Exception as e:
            Logger.error(f"保存邮箱配置失败: {str(e)}")
            messagebox.showerror("错误", f"保存邮箱配置失败: {str(e)}")

    def _create_buttons(self, parent: tk.Frame) -> None:
        """创建按钮区域"""
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=5)
        
        # 登录Cursor按钮
        tk.Button(
            button_frame,
            text="登录Cursor",
            command=self._login_cursor,
            font=("Arial", 12),
            fg="blue"
        ).pack(side=tk.LEFT, padx=5)
        
        # 重置Cursor按钮
        tk.Button(
            button_frame,
            text="重置Cursor",
            command=self._reset_cursor,
            font=("Arial", 12)
        ).pack(side=tk.LEFT, padx=5)
        
        # 一键激活按钮 (原Cursor设置)
        tk.Button(
            button_frame,
            text="一键激活",
            command=self._open_cursor_settings,
            font=("Arial", 12),
            fg="green"
        ).pack(side=tk.LEFT, padx=5)
        
        # 创建新的一行用于测试按钮
        test_frame = tk.Frame(parent)
        test_frame.pack(pady=2)
        
        # 测试按钮
        tk.Button(
            test_frame,
            text="测试",
            command=self._test_cursor,
            font=("Arial", 12),
            fg="red"
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

    def _reset_cursor(self) -> None:
        """重置Cursor"""
        try:
            # 获取自动更新设置
            disable_update = self.disable_auto_update.get()
            
            # 执行重置
            CursorReset.reset_cursor(disable_update=disable_update)
            
            # 更新状态标签
            Logger.info("Cursor重置成功")
            messagebox.showinfo("成功", "Cursor重置完成")
            
        except Exception as e:
            error_msg = f"重置Cursor失败: {str(e)}"
            Logger.error(error_msg)
            messagebox.showerror("错误", error_msg)

    # 测试按钮
    def _test_cursor(self) -> None:

        self.task_running = True
        
        self.open_cursor_setting()
        time.sleep(1)
        loginResult = CursorController.check_cursor_login()

        if(loginResult):
            Logger.info("退出登录 ... ")
            
            CursorController.click_cursor_logout()
            time.sleep(0.5)

        
        self.task_running = False

    def _login_cursor(self) -> None:
        """登录Cursor"""
        # 如果已有任务在运行，不启动新任务
        if self.task_running:
            Logger.warn("有操作正在执行中...")
            return
            
        # 启动新线程执行任务
        thread = threading.Thread(target=self._execute_login_cursor)
        thread.daemon = True
        thread.start()
        
    def _execute_login_cursor(self) -> None:
        """执行登录Cursor操作"""
        try:
            self.task_running = True
            
            # 显示警告窗口
            self.root.after(0, self._show_warning)
            
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="正在登录Cursor..."))
            
            self.sign_cursor_process()

            Logger.info("Cursor 登录成功")
            self.root.after(0, lambda: self.status_label.config(text="Cursor 登录成功"))
            self.root.after(0, lambda: messagebox.showinfo("成功", "Cursor 登录成功"))
            
        except Exception as e:
            error_msg = f"登录过程出错: {str(e)}"
            Logger.error(error_msg, e)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        finally:
            self.task_running = False
            # 隐藏警告窗口
            self.root.after(0, self._hide_warning)

    def _close_cursor(self) -> None:
        """关闭Cursor"""
        try:
            CursorController.close_cursor()
            Logger.info("Cursor已关闭")
            self.status_label.config(text="Cursor已关闭")
        except Exception as e:
            error_msg = f"关闭Cursor失败: {str(e)}"
            Logger.error(error_msg)
            messagebox.showerror("错误", error_msg)

    def _clear_logs(self) -> None:
        """清除日志"""
        Logger.clear()

    def _show_warning(self):
        """显示警告窗口"""
        if self.warning_window:
            return
            
        self.warning_window = Toplevel(self.root)
        self.warning_window.overrideredirect(True)  # 无边框窗口
        self.warning_window.attributes('-topmost', True)  # 置顶
        #self.warning_window.attributes('-alpha', 0.5)  # 设置透明度
        
        # 获取屏幕宽度和高度
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口位置和大小
        window_width = 440  # 减小宽度
        window_height = 65  # 减小高度
        x = (screen_width - window_width) // 2
        y = screen_height - window_height - 50  # 距离底部像素
        self.warning_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # 创建一个Frame作为背景
        bg_frame = tk.Frame(
            self.warning_window
        )
        bg_frame.pack(fill='both', expand=True)
        
        # 添加警告文本
        Label(
            bg_frame,
            text="请确保所有文件已保存！\n请勿操作电脑，喝杯茶休息一下，马上就好☕ \n(按Ctrl+Q中断操作) ",
            fg='#FF0000',  # 鲜艳的红色
            font=('Arial', 14, 'bold')
        ).pack(fill='both', expand=True, padx=5)  # 添加一些内边距

    def _hide_warning(self):
        """隐藏警告窗口"""
        if self.warning_window:
            self.warning_window.destroy()
            self.warning_window = None

    def _handle_interrupt(self) -> None:
        """处理中断热键"""
        if self.task_running:  # 只在任务运行时响应中断
            self.task_running = False
            Logger.info("操作已中断 (Ctrl+Q)")
            self.status_label.config(text="操作已中断")
            self._hide_warning()
            # 确保消息框显示在最前面
            self.root.lift()
            messagebox.showinfo("提示", "操作已中断")

    def check_task_status(self) -> None:
        """检查任务状态"""
        if not self.task_running:
            Logger.error("已终止")
            raise Exception("已终止")

    def open_cursor_setting(self) -> None:
        Logger.info("尝试聚焦Cursor窗口...")
        # 执行设置相关操作
        CursorController.focus_cursor_window()
        Logger.info("窗口聚焦成功，等待界面响应...")
        time.sleep(0.5)  # 增加等待时间
        
        self.check_task_status()
        
        Logger.info("尝试点击设置按钮...")
        CursorController.click_cursor_setting()
        
        self.check_task_status()
        


    def delete_cursor_process(self) -> None:
        """删除Cursor账号"""
        # 检查是否需要启动Cursor
        CursorController.run_cursor()
        Logger.info("Cursor已启动")

        self.check_task_status()
        
        self.open_cursor_setting()
        
        Logger.info("尝试点击管理按钮...")
        time.sleep(1)
        manaResult = CursorController.click_cursor_manager()
        
        self.check_task_status()

        if not manaResult:
            Logger.info("当前账号未登录，尝试登录...")
            CursorController.click_cursor_sign()
            
            self.check_task_status()
            Logger.info("跳转登录页面")
        else:
            Logger.info("跳转管理页面")

        Logger.info("正在打开浏览器...")
        time.sleep(1)

        self.check_task_status()
        #循环判断是否有chrome
        self.chromeOperator.check_chrome_open()

        Logger.info("chrome 浏览器打开完毕...")
        time.sleep(0.5)

        self.check_task_status()
        self.chromeOperator.loop_check_setting()

        time.sleep(0.5)

        self.check_task_status()
        # 删除账号
        self.chromeOperator.delete_cursor_account()
        time.sleep(0.5)

        self.check_task_status()

    # 关闭Cursor进程
    def close_cursor_process(self) -> None:
        """关闭Cursor进程"""
        # 退出登录
        
        self.open_cursor_setting()
        time.sleep(1)
        loginResult = CursorController.check_cursor_login()

        if(loginResult):
            Logger.info("退出登录 ... ")
            
            CursorController.click_cursor_logout()
            time.sleep(0.5)

        self.check_task_status()
        CursorController.focus_cursor_window()
        time.sleep(0.5)
        CursorController.close_cursor()
        time.sleep(1)
        self.check_task_status()

    
    def sure_login_cursor(self, tryTime: int = 8) -> bool:
        
        wait_time = 0
        while wait_time < tryTime:

            try:
                self.chromeOperator.click_cursor_sure_loginin()
                return True
            except Exception as e:
                wait_time += 1
                Logger.info(f"确认登录失败，重试中 ... {wait_time}秒")
                time.sleep(1)

        else:
            error_msg = "确认登录失败 ... "
            Logger.error(error_msg)
            return False


    def loop_cursor_signin(self):

        wait_time = 0
        while wait_time < 20:
            self.open_cursor_setting()
            
            Logger.info("尝试点击 sign in按钮...")
            time.sleep(0.5)

            loginResult = CursorController.check_cursor_login()

            if(loginResult):
                Logger.info("Cursor 已登录，登录完成...")
                break;

            manaResult = CursorController.click_cursor_sign()

            Logger.info("正在打开浏览器...")
            time.sleep(1)

            self.check_task_status()
            #循环判断是否有chrome
            self.chromeOperator.check_chrome_open()
            time.sleep(2)

            self.check_task_status()
            Logger.info("chrome 浏览器打开完毕...")
            time.sleep(1)

            sureResult = self.sure_login_cursor(tryTime = 2)

            if(sureResult):
                Logger.info("Cursor 激活成功 ! ")
                return;

            self.chromeOperator.do_cursor_login()
            
            time.sleep(0.5)
            sureResult = self.sure_login_cursor()

            if(sureResult):
                Logger.info("Cursor 激活成功 ! ")
                return;
            
        else:
            error_msg = "Cursor 登录失败，请手动登录 ... "
            Logger.error(error_msg)
            raise Exception(error_msg)

    def sign_cursor_process(self):
        """登录Cursor"""
        # 检查是否需要启动Cursor
        CursorController.run_cursor(True)
        Logger.info("Cursor已启动")

        self.check_task_status()
        
        self.loop_cursor_signin();
        
        

    def _execute_cursor_settings(self) -> None:
        """执行Cursor设置相关操作"""
        try:
            self.task_running = True
            
            # 显示警告窗口
            self.root.after(0, self._show_warning)
            
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="正在执行操作..."))
            
            if not os.path.exists(CursorConstants.CURSOR_EXE_PATH):
                Logger.error("未找到Cursor程序，请确认Cursor已正确安装。")
                return
            
            # 确认是否继续
            if not messagebox.askyesno("确认", "即将开始操作，请确保所有文件已保存！激活过程中请勿操作电脑。\n按Ctrl+Q可以随时中断操作。\n是否继续？"):
                return
                
            Logger.info("开始打开Cursor设置流程")
            
            try:
                # 删除账号
                self.delete_cursor_process()
                Logger.info("#### 删除账号成功 ... ")
                time.sleep(1)
                # 退出登录
                self.close_cursor_process()
                Logger.info("#### 关闭Cursor 成功 ... ")

                time.sleep(1)

                # 重置 cursor 机器码
                # 获取自动更新设置
                disable_update = self.disable_auto_update.get()
                CursorReset.reset_cursor(disable_update)
                Logger.info("Cursor重置成功")
                time.sleep(1)
                
                self.sign_cursor_process()
                Logger.info("操作完成")
                self.root.after(0, lambda: self.status_label.config(text="操作完成"))
                self.root.after(0, lambda: messagebox.showinfo("成功", "Cursor激活成功"))
                
            except Exception as e:
                Logger.error(f"操作执行出错: ", e)
                raise e
            
        except Exception as e:
            error_msg = f"设置过程出错: {str(e)}"
            Logger.error(error_msg, e)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
        finally:
            self.task_running = False
            # 隐藏警告窗口
            self.root.after(0, self._hide_warning)

    def _open_cursor_settings(self) -> None:
        """打开Cursor设置"""
        # 如果已有任务在运行，不启动新任务
        if self.task_running:
            Logger.warn("有操作正在执行中...")
            return
            
        # 启动新线程执行任务
        thread = threading.Thread(target=self._execute_cursor_settings)
        thread.daemon = True
        thread.start()

    def __del__(self):
        """清理资源"""
        try:
            # 清理警告窗口
            if self.warning_window:
                self.warning_window.destroy()
        except:
            pass
        
             