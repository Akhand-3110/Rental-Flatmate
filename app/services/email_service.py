import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.config import settings

logger = logging.getLogger("uvicorn.error")

def send_notification_email(recipient_email: str, subject: str, text_content: str):
    """
    Sends out transactional alerts using raw SMTP wrappers[cite: 1].
    """
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASS]):
        logger.warning(f"SMTP configurations are missing. Dropping email dispatch: {subject}")
        return

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_FROM
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(text_content, 'plain'))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_PORT == 587:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
            logger.info(f"Notification email dispatched successfully to {recipient_email}")
    except Exception as e:
        logger.error(f"Failed handling outbound transactional email tracking: {str(e)}")