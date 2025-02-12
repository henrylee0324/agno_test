from typing import Optional, List
import os
import mimetypes

from agno.tools import Toolkit
from agno.utils.log import logger

class EmailToolsV2(Toolkit):
    def __init__(
        self,
        sender_name: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_passkey: Optional[str] = None,
    ):
        super().__init__(name="email_tools")
        self.sender_name: Optional[str] = sender_name
        self.sender_email: Optional[str] = sender_email
        self.sender_passkey: Optional[str] = sender_passkey
        self.register(self.email_user)

    def email_user(self, 
                   subject: str, 
                   body: str, 
                   receiver_email: Optional[str] = None,
                   cc: Optional[List[str]] = None,
                   bcc: Optional[List[str]] = None,
                   attachments: Optional[List[str]] = None) -> str:
        """寄送郵件給使用者，可包含附件。

        :param subject: 郵件主旨
        :param body: 郵件內容
        :param receiver_email: 收件者郵件地址
        :param cc: 副本收件者清單
        :param bcc: 密件副本收件者清單
        :param attachments: 附件檔案路徑清單
        :return: 成功返回 "success"，失敗返回 "error: [錯誤訊息]"
        """

        if not receiver_email:
            return "error: No receiver email provided"
        
        try:
            import smtplib
            from email.message import EmailMessage
            from email.mime.application import MIMEApplication
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
        except ImportError:
            logger.error("Required modules not installed")
            raise

        if not self.sender_name:
            return "error: No sender name provided"
        if not self.sender_email:
            return "error: No sender email provided"
        if not self.sender_passkey:
            return "error: No sender passkey provided"

        # 建立多部分郵件
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.sender_email}>"
        msg["To"] = receiver_email

        if cc:
            logger.info(f"Adding CC: {cc}")
            msg["Cc"] = ", ".join(cc)
        if bcc:
            logger.info(f"Adding BCC: {bcc}")
            msg["Bcc"] = ", ".join(bcc)

        # 加入郵件內容
        msg.attach(MIMEText(body, 'plain'))

        # 處理附件
        if attachments:
            logger.info(f"Attaching files: {attachments}")
            for filepath in attachments:
                if not os.path.exists(filepath):
                    return f"error: Attachment not found: {filepath}"
                
                try:
                    with open(filepath, 'rb') as f:
                        filename = os.path.basename(filepath)
                        mime_type, _ = mimetypes.guess_type(filepath)
                        if mime_type is None:
                            mime_type = 'application/octet-stream'
                        
                        part = MIMEApplication(f.read(), _subtype=mime_type.split('/')[-1])
                        part.add_header('Content-Disposition', 'attachment', filename=filename)
                        msg.attach(part)
                except Exception as e:
                    return f"error: Failed to attach file {filepath}: {str(e)}"

        logger.info(f"Sending Email to {receiver_email}")
        
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(self.sender_email, self.sender_passkey)
                smtp.send_message(msg)
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return f"error: {e}"
            
        return "email sent successfully"