class EmailTemplate:
    news_template = """
<p>亲爱的订阅者，您好！</p>
<p style='text-indent:2em'>以下是您订阅的新闻信息:</p>\n"""

    verification_code_template = """
<p>亲爱的用户,您好！</p>
<p style='text-indent:2em'>您正在重设登录密码，验证码为：</p>\n"""


class NewsEmailContent(EmailTemplate):
    def __init__(self, news_dict):
        self.news_dict = news_dict

    @property
    def content(self) -> str:
        if self.news_dict:
            for key in self.news_dict:
                self.news_template += f"<p style='text-indent:2em'><a href='{self.news_dict[key]}'>{key}</a></p>\n"
            return self.news_template


class CodeEmailContent(EmailTemplate):
    def __init__(self, code):
        self.code = code

    @property
    def content(self) -> str:
        self.verification_code_template += f"<p style='text-indent:2em'><h3>&emsp;&emsp;&emsp;{self.code}</h3></p>"
        self.verification_code_template += f"<p style='text-indent:2em'>验证码有效时间：30分钟。<p>"
        return self.verification_code_template
