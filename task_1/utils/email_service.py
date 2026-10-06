import smtplib
from email.message import EmailMessage

from config import Settings


settings = Settings()


def send_mfa_email(recipient: str, mfa_code: str) -> None:
    """Send a temporary administrator MFA code through Ethereal SMTP."""
    message = EmailMessage()
    message["Subject"] = "Voting system MFA code"
    message["From"] = settings.SMTP_FROM
    message["To"] = recipient
    message.set_content(
        f"Your one-time MFA code is: {mfa_code}\n"
        f"It expires in {settings.MFA_CODE_EXPIRE_MINUTES} minutes."
    )

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD.get_secret_value())
        smtp.send_message(message)
