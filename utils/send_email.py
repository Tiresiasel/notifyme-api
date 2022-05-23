import datetime
import json
import logging
import smtplib
from email.mime.text import MIMEText
from utils.email_template import EmailTemplate, CodeEmailContent

logging.getLogger().setLevel(logging.INFO)


class SendEmail:
    def __init__(self, email_class: EmailTemplate):  # subject为news、code
        content = email_class.content
        self.message = MIMEText(content, 'html', 'utf-8')
        with open("config.json", "r") as f:
            self.config = json.load(f)
        self.sender = self.config["sender"]
        self.smtp_host = self.config["smtp_host"]
        self.smtp_password = self.config["smtp_password"]
        self.message["From"] = self.config["from_header"]
        self.message["To"] = self.config["to_header"]
        if email_class.__class__.__name__ == "NewsEmailContent":
            self.message["Subject"] = "Notifyme 投资机构新闻" + datetime.datetime.today().strftime("%Y-%m-%d")
        elif email_class.__class__.__name__ == "CodeEmailContent":
            self.message["Subject"] = "Notifyme 忘记密码"

    def send_email(self, receiver):
        try:
            smtp_obj = smtplib.SMTP()
            smtp_obj.connect(self.smtp_host, 587)  # 网页smtp端口号
            smtp_obj.login(self.sender, self.smtp_password)
            smtp_obj.sendmail(self.sender, receiver, self.message.as_string())
            logging.info("邮件发送成功")
        except smtplib.SMTPException:
            logging.error("无法发送邮件")


if __name__ == '__main__':
    SendEmail(CodeEmailContent("291233")).send_email("1275021527@qq.com")
