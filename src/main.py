"""
一个简单的桌面窗口应用程序，显示Hello World并检测Cursor编辑器状态。

This module creates a desktop window application that displays Hello World
and checks Cursor editor status.
"""
import tkinter as tk
from tkinter import scrolledtext
from typing import NoReturn
import psutil
from datetime import datetime
import os
import winreg
import subprocess
import pyautogui
import time
import pygetwindow as gw
import traceback
from PIL import Image

# 设置pyautogui的安全设置
pyautogui.FAILSAFE = True  # 启用自动防故障功能
pyautogui.PAUSE = 0.5  # 每次操作后暂停0.5秒

# 添加这个常量到文件顶部
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'images')

class Logger:
    """
    日志管理器类，用于处理日志记录和显示。
    
    Attributes:
        log_widget (scrolledtext.ScrolledText): 日志显示组件
    """
    
    def __init__(self, log_widget: scrolledtext.ScrolledText) -> None:
        """
        初始化日志管理器。

        Args:
            log_widget: 用于显示日志的文本组件
        """
        self.log_widget = log_widget
        self.log_widget.config(state='disabled')  # 设置为不可编辑
    
    def log(self, message: str, level: str = "INFO") -> None:
        """
        记录一条日志消息。

        Args:
            message: 日志消息内容
            level: 日志级别，默认为"INFO"
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        # 临时启用编辑以添加新日志
        self.log_widget.config(state='normal')
        self.log_widget.insert(tk.END, log_message)
        self.log_widget.see(tk.END)  # 自动滚动到最新日志
        self.log_widget.config(state='disabled')  # 恢复不可编辑状态
    
    def clear(self) -> None:
        """清除所有日志内容。"""
        self.log_widget.config(state='normal')
        self.log_widget.delete(1.0, tk.END)
        self.log_widget.config(state='disabled')
        self.log("日志已清除")


class HelloWorldApp:
    """
    一个显示Hello World的桌面窗口应用程序类。
    
    Attributes:
        root (tk.Tk): 主窗口实例
        status_label (tk.Label): 状态显示标签
        logger (Logger): 日志管理器实例
    """
    
    def __init__(self) -> None:
        """初始化HelloWorldApp类的新实例。"""
        self.root = tk.Tk()
        self.root.title("Hello World 应用")
        self.root.geometry("600x500")  # 增加窗口大小以适应日志区域
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'images', 'icon', 'icon.png')
        icon = tk.PhotoImage(file=icon_path)
        self.root.iconphoto(True, icon)
        
        self.status_label = None
        self.logger = None
        self._setup_ui()
    
    @staticmethod
    def _is_cursor_running() -> bool:
        """
        检查Cursor编辑器是否正在运行。

        Returns:
            bool: 如果Cursor正在运行返回True，否则返回False
        """
        for proc in psutil.process_iter(['name']):
            try:
                if 'cursor' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    # 启动Cursor编辑器
    def _launch_cursor(self) -> None:
        """
        启动Cursor编辑器。
        使用cmd命令启动Cursor并屏蔽错误输出。
        """
        try:
            # 使用cmd /c start命令来启动程序，并将错误输出重定向到NUL
            cmd = 'cmd /c start "" "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Cursor\\Cursor.exe" 2>NUL'
            # 创建一个新的控制台窗口（隐藏的）来运行命令
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            subprocess.Popen(cmd, 
                           shell=True, 
                           startupinfo=startupinfo,
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            self.logger.log("正在启动Cursor编辑器", "INFO")
        except Exception as e:
            self.logger.log(f"启动Cursor失败: {str(e)}", "ERROR")
    
    # 检查Cursor编辑器状态
    def _check_cursor_status(self) -> None:
        """
        检查Cursor编辑器状态并更新界面显示。
        """
        is_running = self._is_cursor_running()
        status_text = "Cursor编辑器正在运行" if is_running else "Cursor编辑器未运行"
        if self.status_label:
            self.status_label.config(text=status_text)
        
        # 记录检查操作的日志
        self.logger.log(f"检查Cursor状态: {status_text}")
    
    # 清除日志内容
    def _clear_logs(self) -> None:
        """清除日志内容的回调方法。"""
        self.logger.clear()
    
    # 退出Cursor登录状态
    def _logout_cursor(self) -> None:
        """
        退出Cursor的登录状态。
        通过删除登录信息和关闭进程来实现。
        """
        try:
            # 关闭Cursor进程
            for proc in psutil.process_iter(['name']):
                try:
                    if 'cursor' in proc.info['name'].lower():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 删除登录信息
            auth_path = os.path.expandvars(r"%APPDATA%\Cursor\User Data\Default\Local Storage\leveldb")
            if os.path.exists(auth_path):
                import shutil
                shutil.rmtree(auth_path)
            
            self.logger.log("已退出Cursor登录", "INFO")
        except Exception as e:
            self.logger.log(f"退出Cursor登录失败: {str(e)}", "ERROR")
    
    # 聚焦Cursor窗口
    def _focus_cursor_window(self) -> None:
        """
        聚焦Cursor窗口。
        如果窗口最小化则恢复，否则只进行聚焦。
        """
        try:
            # 遍历所有进程查找Cursor
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if 'cursor' in proc.info['name'].lower():
                        pid = proc.info['pid']
                        import win32gui
                        import win32process
                        import win32con
                        
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
                            # 只在窗口最小化时恢复窗口
                            if win32gui.IsIconic(hwnd):
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                            # 将窗口置于前台
                            win32gui.SetForegroundWindow(hwnd)
                            self.logger.log("已成功聚焦Cursor窗口", "INFO")
                            return
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            self.logger.log("未找到Cursor窗口", "ERROR")
            
        except Exception as e:
            self.logger.log(f"聚焦Cursor窗口失败: {str(e)}", "ERROR")


    # 点击Cursor设置按钮
    def _click_cursor_button(self, button_image_name: str) -> bool:
        """
        在Cursor编辑器中查找并点击指定的按钮。

        Args:
            button_image_name: 按钮图像的文件名
        
        Returns:
            bool: 是否成功点击按钮
        """
        try:
            button_image_path = os.path.join(RESOURCES_DIR, button_image_name)
            
            if not os.path.exists(button_image_path):
                self.logger.log(f"按钮图片不存在: {button_image_path}", "ERROR")
                return False
                
            # 获取当前活动窗口
            window = gw.getActiveWindow()
            if not window or 'cursor' not in window.title.lower():
                self.logger.log("当前窗口不是Cursor", "WARNING")
                return False
            
            # 计算搜索区域，确保不超出屏幕范围
            search_region = (
                max(0, window.right - 800),  # 搜索宽度800
                max(0, window.top),
                min(800, window.right),
                min(200, window.height)  # 搜索高度200
            )

            # 保存调试截图
            screenshot = pyautogui.screenshot(region=search_region)
            os.makedirs("./tmp", exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"./tmp/search_region_{timestamp}.png"
            screenshot.save(screenshot_path)

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
                        pyautogui.moveTo(button_center.x, button_center.y, duration=0.2)
                        pyautogui.click()
                        self.logger.log("成功点击设置按钮", "INFO")
                        return True
                
                return False
                
            except Exception as e:
                self.logger.log(f"查找按钮失败: {str(e)}", "WARNING")
                return False
            
        except Exception as e:
            self.logger.log(f"点击按钮失败: {str(e)}", "ERROR")
            return False
    
    def _show_activation_message(self) -> tk.Toplevel:
        """
        显示激活提示窗口。
        
        Returns:
            tk.Toplevel: 提示窗口实例
        """
        # 创建提示窗口
        msg_window = tk.Toplevel(self.root)
        msg_window.overrideredirect(True)  # 移除窗口边框
        msg_window.attributes('-topmost', True)  # 置顶显示
        
        # 设置窗口样式
        msg_window.configure(bg='black')
        
        # 创建标签
        label = tk.Label(
            msg_window,
            text="激活中，请勿操作电脑",
            font=("Arial", 20, "bold"),
            fg="red",  # 改为红色文字
            bg="black",
            padx=40,
            pady=10
        )
        label.pack()
        
        # 移动到屏幕顶部
        screen_width = self.root.winfo_screenwidth()
        window_width = 300
        window_height = 50
        x = (screen_width - window_width) // 2
        y = 0  # 放置在顶部
        msg_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        return msg_window

    def _open_cursor_settings(self) -> None:
        """
        打开Cursor设置的完整流程。
        """
        try:
            # 显示提示弹窗
            from tkinter import messagebox
            result = messagebox.showwarning(
                "操作提示",
                "激活过程中，请勿操作电脑",
                icon='warning'
            )
            
            if result == 'ok':
                self.logger.log("开始打开Cursor设置流程", "INFO")
                
                # 检查Cursor是否运行
                if not self._is_cursor_running():
                    self.logger.log("Cursor未运行，正在启动...", "INFO")
                    self._launch_cursor()
                    time.sleep(5)
                
                # 聚焦窗口
                self._focus_cursor_window()
                time.sleep(1)
                
                # 尝试不同主题的按钮图片
                button_images = [
                    "button/setting-button-light.png",
                    "button/setting-button-dark.png"
                ]
                
                for image in button_images:
                    if self._click_cursor_button(image):
                        break
                
        except Exception as e:
            self.logger.log(f"打开设置失败: {str(e)}", "ERROR")
    
    def _setup_ui(self) -> None:
        """设置用户界面组件。"""
        # 创建上半部分的Frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建主标签
        main_label = tk.Label(
            top_frame,
            text="Hello World!",
            font=("Arial", 24)
        )
        main_label.pack(expand=True, pady=10)
        
        # 创建状态标签
        self.status_label = tk.Label(
            top_frame,
            text="点击按钮检查Cursor状态",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=5)
        
        # 创建按钮Frame
        button_frame = tk.Frame(top_frame)
        button_frame.pack(pady=5)
        
        # 创建检查按钮
        check_button = tk.Button(
            button_frame,
            text="检查Cursor状态",
            command=self._check_cursor_status,
            font=("Arial", 12)
        )
        check_button.pack(side=tk.LEFT, padx=5)
        
        # 创建Evil按钮
        evil_button = tk.Button(
            button_frame,
            text="Evil",
            command=self._launch_cursor,
            font=("Arial", 12),
            fg="red"
        )
        evil_button.pack(side=tk.LEFT, padx=5)
        
        # 创建登出按钮
        logout_button = tk.Button(
            button_frame,
            text="退出Cursor登录",
            command=self._logout_cursor,
            font=("Arial", 12),
            fg="blue"
        )
        logout_button.pack(side=tk.LEFT, padx=5)
        
        # 在button_frame中添加新按钮
        click_button = tk.Button(
            button_frame,
            text="Cursor设置",
            command=self._open_cursor_settings,
            font=("Arial", 12),
            fg="green"
        )
        click_button.pack(side=tk.LEFT, padx=5)
        
        # 创建日志操作区域
        log_control_frame = tk.Frame(self.root)
        log_control_frame.pack(fill=tk.X, padx=10)
        
        # 创建日志区域标签
        log_label = tk.Label(
            log_control_frame,
            text="操作日志",
            font=("Arial", 12)
        )
        log_label.pack(side=tk.LEFT, pady=(10, 5))
        
        # 创建清屏按钮
        clear_button = tk.Button(
            log_control_frame,
            text="清除日志",
            command=self._clear_logs,
            font=("Arial", 10)
        )
        clear_button.pack(side=tk.RIGHT, pady=(10, 5))
        
        # 创建日志文本区域
        log_widget = scrolledtext.ScrolledText(
            self.root,
            height=10,
            font=("Courier", 10),
            state='disabled'  # 设置为不可编辑
        )
        log_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 初始化日志管理器
        self.logger = Logger(log_widget)
        self.logger.log("应用程序启动")
    
    def run(self) -> NoReturn:
        """运行应用程序的主循环。"""
        self.logger.log("开始运行主循环")
        self.root.mainloop()


def main() -> None:
    """程序入口点。"""
    app = HelloWorldApp()
    app.run()


if __name__ == "__main__":
    main() 