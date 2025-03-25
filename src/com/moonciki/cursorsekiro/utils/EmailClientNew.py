import imaplib
import email
from email.header import decode_header


# Outlook IMAP服务器配置
IMAP_SERVER = "outlook.office365.com"
IMAP_PORT = 993
EMAIL = "ysqcursor"
PASSWORD = "19911024YSQ"

def clean(text):
    """简单的文本清理函数，用于处理邮件主题"""
    return "".join(c if c.isalnum() else "_" for c in text)

def fetch_emails():
    try:
        # 连接到IMAP服务器
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        
        mail._debug = 4  # 显示详细调试信息

        # 登录
        mail.login(EMAIL, PASSWORD)
        print("登录成功")
        
        # 选择邮箱（默认收件箱）
        mail.select("inbox")
        
        # 搜索所有邮件（也可以使用其他标准如'UNSEEN'）
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("没有找到邮件")
            return
        
        # 将邮件ID转换为列表
        messages = messages[0].split()
        
        # 获取最新的5封邮件（从最新到最旧）
        for mail_id in messages[-5:][::-1]:
            # 获取邮件
            status, msg_data = mail.fetch(mail_id, "(RFC822)")
            if status != "OK":
                print(f"获取邮件 {mail_id} 失败")
                continue
            
            # 解析邮件内容
            msg = email.message_from_bytes(msg_data[0][1])
            
            # 解码邮件主题
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            
            # 解码发件人
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding if encoding else "utf-8")
            
            print("\n" + "="*50)
            print(f"主题: {subject}")
            print(f"发件人: {From}")
            print(f"日期: {msg.get('Date')}")
            
            # 提取邮件正文
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        print("\n正文:")
                        print(body)
                    elif "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            filename = decode_header(filename)[0][0]
                            if isinstance(filename, bytes):
                                filename = filename.decode()
                            print(f"附件: {filename}")
            else:
                content_type = msg.get_content_type()
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    print("\n正文:")
                    print(body)
            
            print("="*50 + "\n")
        
        # 关闭连接
        mail.logout()
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    fetch_emails()