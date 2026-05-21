import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional


SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "tabwatch@example.com")


def build_email(
    recipient: str,
    subject: str,
    plain_text: str,
    html_body: Optional[str] = None,
) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = recipient

    msg.attach(MIMEText(plain_text, "plain"))
    if html_body:
        msg.attach(MIMEText(html_body, "html"))

    return msg


def send_email(
    recipient: str,
    subject: str,
    plain_text: str,
    html_body: Optional[str] = None,
) -> bool:
    """
    Send an email via SMTP. Returns True on success, False on failure.
    """
    msg = build_email(recipient, subject, plain_text, html_body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            if SMTP_PORT == 587:
                server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, [recipient], msg.as_string())
        return True
    except smtplib.SMTPException as exc:
        print(f"[email_sender] Failed to send email to {recipient}: {exc}")
        return False


def send_weekly_digest_email(
    recipient: str,
    digest_text: str,
    week_start: datetime,
) -> bool:
    week_label = week_start.strftime("%B %d, %Y")
    subject = f"Your TabWatch weekly digest — week of {week_label}"
    return send_email(recipient, subject, digest_text)
