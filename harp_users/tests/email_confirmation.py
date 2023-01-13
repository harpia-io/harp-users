import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from microservice_template_core.tools.logger import get_logger
import harp_users.settings as settings
from harp_users.logic.email_template import template
import ssl
from harp_users.logic.get_bot_config import bot_config

bot_config = bot_config(bot_name='email')
logger = get_logger()

ctx = ssl.create_default_context()

smtp = smtplib.SMTP_SSL(settings.SMTP_HOST, port=settings.SMTP_PORT)
smtp.login(user=bot_config['EMAIL_USER'], password=bot_config['EMAIL_PASSWORD'])
