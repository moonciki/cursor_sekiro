"""
邮件客户端模块，用于登录126邮箱并接收邮件。
"""
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

from com.moonciki.cursorsekiro.utils.email_constants import EmailConstants
from com.moonciki.cursorsekiro.logger import Logger


class EmailClient:
    """
    邮件客户端类，提供邮件收发功能。
    
    主要功能：
    1. 连接到邮件服务器
    2. 获取邮件列表
    3. 发送邮件
    4. 搜索邮件
    """
    
    # 常见邮箱服务器配置
    EMAIL_SERVERS = {
        "126.com": {
            "imap_server": "imap.126.com",
            "imap_port": 993,
            "smtp_server": "smtp.126.com",
            "smtp_port": 465  # 126邮箱使用465端口进行SSL加密
        },
        "163.com": {
            "imap_server": "imap.163.com",
            "imap_port": 993,
            "smtp_server": "smtp.163.com", 
            "smtp_port": 465
        },
        "outlook.com": {
            "imap_server": "outlook.office365.com",
            "imap_port": 993,
            "smtp_server": "smtp-mail.outlook.com",
            "smtp_port": 587
        },
        "gmail.com": {
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587
        },
        "qq.com": {
            "imap_server": "imap.qq.com",
            "imap_port": 993,
            "smtp_server": "smtp.qq.com",
            "smtp_port": 587
        }
    }
    
    def __init__(self):
        """
        初始化邮件客户端。
        """
        self.email_address = EmailConstants.get_email()
        self.password = EmailConstants.get_email_password()  # 对于126邮箱，这里需要使用授权码而不是登录密码
        self.imap_client = None
        self.smtp_client = None
        self.server_config = self._get_server_config()
    
    def _get_server_config(self) -> Dict[str, Any]:
        """
        根据邮箱地址获取对应的服务器配置。
        
        Returns:
            包含服务器配置的字典
        """
        if not self.email_address:
            return self.EMAIL_SERVERS.get("outlook.com")  # 默认使用Outlook配置
            
        # 从邮箱地址中提取域名
        domain_match = re.search(r'@([^@]+)$', self.email_address)
        if not domain_match:
            return self.EMAIL_SERVERS.get("outlook.com")
            
        domain = domain_match.group(1).lower()
        
        # 查找匹配的服务器配置
        for key, config in self.EMAIL_SERVERS.items():
            if domain.endswith(key):
                Logger.info(f"使用 {key} 的邮箱服务器配置")
                return config
                
        # 如果没有找到匹配的配置，使用默认配置
        Logger.info(f"未找到 {domain} 的服务器配置，使用默认Outlook配置")
        return self.EMAIL_SERVERS.get("outlook.com")
    
    def connect(self) -> bool:
        """
        连接到邮件服务器。
        
        Returns:
            连接是否成功
        """
        if not self.email_address or not self.password:
            Logger.error("邮箱配置不完整，无法连接")
            self._show_error_dialog("邮箱配置不完整", 
                "请先完成邮箱配置再尝试连接。\n"
                "注意：126邮箱需要使用授权码而不是登录密码")
            return False
            
        try:
            # 连接IMAP服务器（用于接收邮件）
            imap_server = self.server_config.get("imap_server")
            imap_port = self.server_config.get("imap_port")
            
            # 创建更安全的 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            Logger.info(f"尝试连接到IMAP服务器: {imap_server}:{imap_port}")
            self.imap_client = imaplib.IMAP4_SSL(imap_server, imap_port, ssl_context=ssl_context)
            
            # 设置更长的超时时间
            self.imap_client.socket().settimeout(30)
            
            # 尝试登录
            try:
                Logger.info(f"尝试使用账户 {self.email_address} 登录")
                
                # 设置 IMAP ID 信息
                imap_id = (
                    "name", "CursorSekiro",
                    "version", "1.0.0",
                    "vendor", "MoonCiki",
                    "support-email", "support@moonciki.com",
                    "contact", self.email_address,
                    "date", datetime.now().strftime("%Y-%m-%d"),
                    "os", "Windows",  # 添加操作系统信息
                    "os-version", "10",  # 添加系统版本
                    "command", "select"  # 指定命令
                )
                
                # 先发送 ID 信息
                try:
                    Logger.info("发送 IMAP ID 信息...")
                    typ, data = self.imap_client._simple_command('ID', '("' + '" "'.join(imap_id) + '")')
                    if typ == 'OK':
                        Logger.info("IMAP ID 信息发送成功")
                        if data and data[0]:
                            server_id = data[0].decode('utf-8')
                            Logger.info(f"服务器 ID 信息: {server_id}")
                    else:
                        Logger.info(f"IMAP ID 命令未成功: {typ} {data if data else ''}")
                except Exception as e:
                    Logger.info(f"发送 IMAP ID 信息时出错: {str(e)}")
                
                # 尝试登录
                self.imap_client.login(self.email_address, self.password)
                Logger.info("IMAP登录成功")
                
                # 选择收件箱
                try:
                    status, data = self.imap_client.select('INBOX')
                    if status != 'OK':
                        Logger.error(f"选择收件箱失败: {data}")
                    else:
                        Logger.info("成功选择收件箱")
                except Exception as e:
                    Logger.error(f"选择收件箱时出错: {str(e)}")
                
                return True
                
            except imaplib.IMAP4.error as e:
                Logger.error("IMAP登录失败: ", e)
                error_msg = str(e)
                if "LOGIN failed" in error_msg or "Unsafe Login" in error_msg:
                    Logger.error(f"登录失败: {error_msg}")
                    self._show_error_dialog("邮箱登录失败", 
                        "请确保以下几点:\n"
                        "1. 用户名正确\n"
                        "2. 使用的是授权码而不是登录密码\n"
                        "3. 邮箱账户已开启IMAP协议\n"
                        "4. 授权码未过期\n"
                        "5. 如果仍然失败，请联系邮箱客服")
                else:
                    Logger.error(f"IMAP登录失败: {error_msg}")
                    self._show_error_dialog("邮箱登录失败", f"IMAP登录失败: {error_msg}")
                return False
            
        except Exception as e:
            Logger.error(f"连接邮件服务器失败: {str(e)}")
            self._show_error_dialog("连接失败", "无法连接到邮件服务器，请检查网络连接和服务器配置。")
            return False
    
    def disconnect(self) -> None:
        """
        断开与邮件服务器的连接。
        """
        try:
            if self.imap_client:
                self.imap_client.logout()
                self.imap_client = None
                
            if self.smtp_client:
                self.smtp_client.quit()
                self.smtp_client = None
                
            Logger.info("已断开邮件服务器连接")
        except Exception as e:
            Logger.error(f"断开邮件服务器连接时出错: {str(e)}")
    
    def get_folders(self) -> List[str]:
        """
        获取邮箱中的文件夹列表。
        
        Returns:
            文件夹名称列表
        """
        if not self.imap_client:
            if not self.connect():
                return []
                
        try:
            # 获取所有文件夹
            status, folder_list = self.imap_client.list()
            if status != "OK":
                Logger.error("获取邮箱文件夹失败")
                return []
                
            folders = []
            for folder in folder_list:
                if isinstance(folder, bytes):
                    # 解析文件夹名称
                    folder_str = folder.decode('utf-8')
                    # 提取文件夹名称
                    match = re.search(r'"([^"]+)"$', folder_str)
                    if match:
                        folder_name = match.group(1)
                        folders.append(folder_name)
                    
            Logger.info(f"成功获取 {len(folders)} 个邮箱文件夹")
            return folders
        except Exception as e:
            Logger.error(f"获取邮箱文件夹时出错: {str(e)}")
            return []
    
    def get_latest_emails(self, limit: int = 10, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        获取最新的邮件。
        
        Args:
            limit: 获取的邮件数量限制
            unread_only: 是否只获取未读邮件
            
        Returns:
            包含邮件信息的字典列表
        """
        if not self.imap_client:
            if not self.connect():
                return []
        
        emails = []
        try:
            # 直接选择 INBOX
            Logger.info("选择收件箱...")

            status, messages = self.imap_client.select("INBOX")  # 不传参数默认选择 INBOX
            if status != "OK":
                Logger.error("无法选择收件箱")
                return []
            
            # 获取邮件的UID
            search_criteria = "UNSEEN" if unread_only else "ALL"
            status, message_ids = self.imap_client.search(None, search_criteria)
            if status != "OK":
                Logger.error(f"搜索邮件失败，条件: {search_criteria}")
                return []
            
            # 获取最新的N封邮件
            message_id_list = message_ids[0].split()
            message_id_list = message_id_list[-limit:] if len(message_id_list) > limit else message_id_list
            
            # 逆序处理，最新的邮件在前
            for message_id in reversed(message_id_list):
                status, msg_data = self.imap_client.fetch(message_id, "(RFC822)")
                if status != "OK":
                    continue
                
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # 解析邮件内容
                subject = self._decode_header(email_message["Subject"])
                from_address = self._decode_header(email_message["From"])
                date_str = email_message["Date"]
                
                # 获取邮件正文
                body = self._get_email_body(email_message)
                
                # 解析日期
                try:
                    date = email.utils.parsedate_to_datetime(date_str)
                except:
                    date = datetime.now()
                
                emails.append({
                    "id": message_id.decode(),
                    "subject": subject,
                    "from": from_address,
                    "date": date,
                    "body": body
                })
            
            Logger.info(f"成功获取 {len(emails)} 封最新邮件")
            return emails
        except Exception as e:
            Logger.error(f"获取邮件时出错: {str(e)}")
            return []
    
    def send_email(self, to_address: str, subject: str, body: str, html: bool = False) -> bool:
        """
        发送邮件。
        
        Args:
            to_address: 收件人地址
            subject: 邮件主题
            body: 邮件正文
            html: 是否为HTML格式
            
        Returns:
            发送是否成功
        """
        if not self.email_address or not self.password:
            Logger.error("邮箱配置不完整，无法发送邮件")
            self._show_error_dialog("邮箱配置不完整", "请先完成邮箱配置再尝试发送邮件。")
            return False
        
        try:
            # 创建SMTP客户端（使用SSL）
            Logger.info(f"连接SMTP服务器: {self.server_config.get('smtp_server')}:{self.server_config.get('smtp_port')}")
            self.smtp_client = smtplib.SMTP_SSL(
                self.server_config.get('smtp_server'), 
                self.server_config.get('smtp_port')
            )
            
            try:
                Logger.info(f"尝试SMTP登录: {self.email_address}")
                self.smtp_client.login(self.email_address, self.password)
            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"SMTP认证失败: {str(e)}"
                Logger.error(error_msg)
                self._show_error_dialog("邮箱登录失败", 
                    "请确保以下几点:\n"
                    "1. 用户名正确\n"
                    "2. 使用的是授权码而不是登录密码\n"
                    "3. 邮箱账户已开启SMTP协议\n"
                    "4. 授权码未过期")
                return False
            
            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = self.email_address
            msg["To"] = to_address
            msg["Subject"] = subject
            
            # 添加邮件正文
            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type, "utf-8"))
            
            # 发送邮件
            self.smtp_client.sendmail(self.email_address, to_address, msg.as_string())
            self.smtp_client.quit()
            
            Logger.info(f"邮件已成功发送至 {to_address}")
            return True
        except Exception as e:
            error_msg = f"发送邮件失败: {str(e)}"
            Logger.error(error_msg)
            self._show_error_dialog("发送邮件失败", f"发送邮件时出现错误: {str(e)}")
            return False
    
    def search_emails(self, criteria: str, folder: str = "INBOX", limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索邮件。
        
        Args:
            criteria: 搜索条件，例如 'SUBJECT "重要通知"'
            folder: 邮件文件夹
            limit: 结果数量限制
            
        Returns:
            符合条件的邮件列表
        """
        if not self.imap_client:
            if not self.connect():
                return []
        
        emails = []
        try:
            # 选择邮件文件夹
            status, messages = self.imap_client.select(folder)
            if status != "OK":
                return []
            
            # 搜索邮件
            status, message_ids = self.imap_client.search(None, criteria)
            if status != "OK":
                return []
            
            # 获取搜索结果
            message_id_list = message_ids[0].split()
            message_id_list = message_id_list[-limit:] if len(message_id_list) > limit else message_id_list
            
            for message_id in reversed(message_id_list):
                status, msg_data = self.imap_client.fetch(message_id, "(RFC822)")
                if status != "OK":
                    continue
                
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # 解析邮件内容
                subject = self._decode_header(email_message["Subject"])
                from_address = self._decode_header(email_message["From"])
                date_str = email_message["Date"]
                
                # 获取邮件正文
                body = self._get_email_body(email_message)
                
                # 解析日期
                try:
                    date = email.utils.parsedate_to_datetime(date_str)
                except:
                    date = datetime.now()
                
                emails.append({
                    "id": message_id.decode(),
                    "subject": subject,
                    "from": from_address,
                    "date": date,
                    "body": body
                })
            
            return emails
        except Exception as e:
            Logger.error(f"搜索邮件时出错: {str(e)}")
            return []
    
    def _decode_header(self, header: Optional[str]) -> str:
        """
        解码邮件头信息。
        
        Args:
            header: 邮件头信息
            
        Returns:
            解码后的文本
        """
        if not header:
            return ""
            
        try:
            decoded_header = email.header.decode_header(header)
            result = ""
            
            for data, charset in decoded_header:
                if isinstance(data, bytes):
                    if charset:
                        result += data.decode(charset, errors="replace")
                    else:
                        result += data.decode("utf-8", errors="replace")
                else:
                    result += str(data)
                    
            return result
        except Exception as e:
            Logger.error(f"解码邮件头信息失败: {str(e)}")
            return str(header)
    
    def _get_email_body(self, email_message: email.message.Message) -> str:
        """
        获取邮件正文内容，只获取文本内容。
        
        Args:
            email_message: 邮件对象
            
        Returns:
            邮件正文文本
        """
        if email_message.is_multipart():
            # 如果邮件包含多个部分，递归获取文本内容
            for part in email_message.walk():
                content_type = part.get_content_type()
                
                # 只获取文本内容
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True)
                        charset = part.get_content_charset() or "utf-8"
                        return body.decode(charset, errors="replace")
                    except Exception as e:
                        Logger.error(f"解析邮件正文失败: {str(e)}")
                        continue
            
            # 如果没有找到纯文本，尝试从HTML中提取
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    try:
                        body = part.get_payload(decode=True)
                        charset = part.get_content_charset() or "utf-8"
                        # 可以在这里添加HTML到纯文本的转换
                        return body.decode(charset, errors="replace")
                    except Exception as e:
                        Logger.error(f"解析邮件HTML正文失败: {str(e)}")
                        continue
            
            return "无法解析邮件内容"
        else:
            # 如果邮件只有一个部分
            try:
                body = email_message.get_payload(decode=True)
                charset = email_message.get_content_charset() or "utf-8"
                return body.decode(charset, errors="replace")
            except Exception as e:
                Logger.error(f"解析单部分邮件正文失败: {str(e)}")
                return "无法解析邮件内容"

    def _show_error_dialog(self, title: str, message: str) -> None:
        """
        显示错误对话框。
        
        Args:
            title: 对话框标题
            message: 错误信息
        """
        try:
            # 尝试导入QMessageBox
            from PyQt5.QtWidgets import QMessageBox, QApplication
            import sys
            
            # 确保有QApplication实例
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            # 创建并显示错误对话框
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
        except ImportError:
            # 如果无法导入PyQt5，则只记录日志
            Logger.error(f"无法显示错误对话框: {title} - {message}")
        except Exception as e:
            Logger.error(f"显示错误对话框时出错: {str(e)}")
