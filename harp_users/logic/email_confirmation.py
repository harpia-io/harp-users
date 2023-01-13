import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from microservice_template_core.tools.logger import get_logger
import harp_users.settings as settings
from harp_users.logic.email_template import template
import ssl
from harp_users.logic.get_bot_config import bot_config

logger = get_logger()


class CreateEmail(object):
    def __init__(self, recipient_name, token, username):
        self.recipient_name = recipient_name
        self.username = username
        self.token = token
        self.smtp = None
        self.event_id = None
        self.bot_config = bot_config(bot_name='email')

    def define_invite_confirmation_url(self):
        if settings.DOCKER_SERVER_IP:
            confirmation_url = f"http://{settings.DOCKER_SERVER_IP}/#/user-registration?email={self.recipient_name}&token={self.token}&username={self.username}"
        else:
            confirmation_url = f"https://{settings.SERVICE_NAMESPACE}.harpia.io/#/user-registration?email={self.recipient_name}&token={self.token}&username={self.username}"

        return confirmation_url

    def email_template(self):
        html = template.replace("{confirmation_endpoint}", self.define_invite_confirmation_url())

        return html

    def prepare_email(self):
        msgroot = MIMEMultipart('related')
        msgroot['From'] = self.bot_config['EMAIL_USER']
        msgroot['To'] = self.recipient_name
        msgroot['Subject'] = 'Invite confirmation'

        logger.info(
            msg=f"Email should be created",
            extra={'tags': {
                "event_id": self.event_id
            }})

        msgroot["Message-ID"] = email.utils.make_msgid()
        msgroot.preamble = 'This is a multi-part message in MIME format.'
        msgalternative = MIMEMultipart('alternative')
        msgroot.attach(msgalternative)
        msgtext = MIMEText(self.email_template(), 'html')

        msgalternative.attach(msgtext)

        return msgroot

    def smtp_connection(self):
        ctx = ssl.create_default_context()
        try:
            self.smtp = smtplib.SMTP_SSL(settings.SMTP_HOST, port=settings.SMTP_PORT, context=ctx)
            self.smtp.login(user=self.bot_config['EMAIL_USER'], password=self.bot_config['EMAIL_PASSWORD'])
            logger.info(
                msg=f"Connected to SMTP",
                extra={'tags': {
                        "event_id": self.event_id
                    }})
        except Exception as err:
            logger.error(
                msg=f"Can`t connect to SMTP:{err}",
                extra={'tags': {
                        "event_id": self.event_id
                    }})

    def create_email(self):
        self.smtp_connection()
        try:
            msgroot = self.prepare_email()

            self.smtp.sendmail(self.bot_config['EMAIL_USER'], self.recipient_name, msgroot.as_string())
            self.smtp.close()

        except (smtplib.SMTPServerDisconnected, smtplib.SMTPSenderRefused) as err:
            logger.error(
                msg=f"Can`t send email: {err}",
                extra={'tags': {
                        "event_id": self.event_id
                    }})

        return 'success'


# some_class = CreateEmail(recipient_name='nkondratyk93@gmail.com', token='ololo', username='nkondratyk')
# some_class.create_email()
