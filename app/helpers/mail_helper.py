from flask_mail import Message

from app import mail
from settings import settings


class MailHelper:
    def __init__(self):
        self.sender = settings.MAIL_USERNAME

    def send_mail(self, title: str, message: str, recipients: list) -> bool:
        msg = Message(title, sender=self.sender, recipients=recipients)
        msg.body = message
        mail.send(msg)

        return True
