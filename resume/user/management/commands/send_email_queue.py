
import datetime as dt
import os
import time
from email import message_from_file

from core.config import WebConfig
from core.logger import FileRotatingLogger
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.core.management.base import BaseCommand

email_logger = FileRotatingLogger(
    WebConfig.LOG_DIR, 'emails.log', debug=settings.DEBUG
).get_logger()


class Command(BaseCommand):
    help = 'Фоновая отправка писем из папки EMAIL_DIR'

    def handle(self: 'Command', *args: tuple, **options: dict) -> None:
        while True:
            start_time = time.time()
            self._send_emails()
            elapsed_time = time.time() - start_time
            wait_time = max(
                0, WebConfig.MIN_WAIT_EMAIL.total_seconds() - elapsed_time)
            time.sleep(wait_time)

    @staticmethod
    def clean_email_footer(text: str) -> str:
        lines = text.strip().splitlines()
        while lines and lines[-1].strip('- \t') == '':
            lines.pop()

        return '\n'.join(lines)

    def _send_emails(self: 'Command') -> None:
        for filename in os.listdir(WebConfig.EMAIL_DIR):
            path = os.path.join(WebConfig.EMAIL_DIR, filename)

            if not path.endswith('.log') or not os.path.isfile(path):
                continue

            file_ctime = dt.datetime.fromtimestamp(os.path.getctime(path))
            if dt.datetime.now() - file_ctime > WebConfig.MAX_EMAIL_AGE:
                os.remove(path)
                continue

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    msg = message_from_file(f)

                subject = msg.get('Subject', '')
                from_email = msg.get('From')
                to = msg.get('To').split(',')
                body = self.clean_email_footer(msg.get_payload())

                connection = get_connection(
                    'django.core.mail.backends.smtp.EmailBackend')
                email = EmailMessage(
                    subject, body, from_email, to, connection=connection)
                email.send(fail_silently=False)
                os.remove(path)

            except Exception as e:
                email_logger.exception(e)
