"""
邮件客户端模块，用于登录Outlook邮箱并接收邮件。
"""
import imaplib
import email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        },
        "163.com": {
            "imap_server": "imap.163.com",
            "imap_port": 993,
            "smtp_server": "smtp.163.com",
            "smtp_port": 25
        }
    }
    
    def __init__(self):
        """
        初始化邮件客户端。
        """
        self.email_address = EmailConstants.get_email()
        self.password = EmailConstants.get_email_password()
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
            self._show_error_dialog("邮箱配置不完整", "请先完成邮箱配置再尝试连接。")
            return False
            
        try:
            # 连接IMAP服务器（用于接收邮件）
            imap_server = self.server_config.get("imap_server")
            imap_port = self.server_config.get("imap_port")
            
            Logger.info(f"尝试连接到IMAP服务器: {imap_server}:{imap_port}")
            self.imap_client = imaplib.IMAP4_SSL(imap_server, imap_port)
            
            # 尝试登录
            try:
                Logger.info(f"尝试使用账户 {self.email_address} 登录")
                self.imap_client.login(self.email_address, self.password)
                Logger.info("IMAP登录成功")
            except imaplib.IMAP4.error as e:
                
                Logger.error("IMAP登录失败: ", e)
                error_msg = str(e)
                if "LOGIN failed" in error_msg:
                    Logger.error(f"登录失败: 用户名或密码错误。错误详情: {error_msg}")
                    self._show_error_dialog("邮箱登录失败", 
                        "请确保以下几点:\n"
                        "1. 用户名和密码正确\n"
                        "2. 邮箱账户已开启IMAP协议\n"
                        "3. 如使用双重验证，请使用应用密码而非普通密码")
                else:
                    Logger.error(f"IMAP登录失败: {error_msg}")
                    self._show_error_dialog("邮箱登录失败", f"IMAP登录失败: {error_msg}")
                return False
            
            Logger.info(f"成功连接到邮件服务器: {self.email_address}")
            return True
        except Exception as e:
            Logger.error(f"连接邮件服务器失败: {str(e)}")
            Logger.info("请检查网络连接和服务器配置")
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
    
    def get_latest_emails(self, folder: str = "INBOX", limit: int = 10, unread_only: bool = False) -> List[Dict[str, Any]]:
        """
        获取最新的邮件。
        
        Args:
            folder: 邮件文件夹，默认为收件箱
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
            # 选择邮件文件夹
            status, messages = self.imap_client.select(folder)
            if status != "OK":
                Logger.error(f"选择邮件文件夹 {folder} 失败")
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
                
                # 检查是否有附件
                has_attachment = False
                attachments = []
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') and 'attachment' in part.get('Content-Disposition'):
                        has_attachment = True
                        filename = self._decode_header(part.get_filename())
                        attachments.append(filename)
                
                # 检查是否已读
                status, flags_data = self.imap_client.fetch(message_id, "(FLAGS)")
                flags = flags_data[0].decode()
                is_read = "\\Seen" in flags
                
                emails.append({
                    "id": message_id.decode(),
                    "subject": subject,
                    "from": from_address,
                    "date": date,
                    "body": body,
                    "is_read": is_read,
                    "has_attachment": has_attachment,
                    "attachments": attachments
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
            # 创建SMTP客户端
            Logger.info(f"连接SMTP服务器: {self.server_config.get('smtp_server')}:{self.server_config.get('smtp_port')}")
            self.smtp_client = smtplib.SMTP(self.server_config.get('smtp_server'), self.server_config.get('smtp_port'))
            self.smtp_client.ehlo()
            self.smtp_client.starttls()
            
            try:
                Logger.info(f"尝试SMTP登录: {self.email_address}")
                self.smtp_client.login(self.email_address, self.password)
            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"SMTP认证失败: {str(e)}"
                Logger.error(error_msg)
                self._show_error_dialog("邮箱登录失败", 
                    "请确保以下几点:\n"
                    "1. 用户名和密码正确\n"
                    "2. 邮箱账户已开启SMTP协议\n"
                    "3. 如使用双重验证，请使用应用密码而非普通密码")
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
        获取邮件正文内容。
        
        Args:
            email_message: 邮件对象
            
        Returns:
            邮件正文
        """
        if email_message.is_multipart():
            # 如果邮件包含多个部分，递归获取文本内容
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # 跳过附件
                if "attachment" in content_disposition:
                    continue
                
                # 获取文本内容
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True)
                        charset = part.get_content_charset() or "utf-8"
                        return body.decode(charset, errors="replace")
                    except Exception as e:
                        Logger.error(f"解析邮件正文失败: {str(e)}")
                        continue
            
            # 如果没有找到纯文本内容，尝试获取HTML内容
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/html":
                    try:
                        body = part.get_payload(decode=True)
                        charset = part.get_content_charset() or "utf-8"
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
