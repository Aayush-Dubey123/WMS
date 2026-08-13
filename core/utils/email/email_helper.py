"""
email_helper.py — Async email sending via Gmail SMTP.

Why async SMTP?
  FastAPI is async — using a blocking SMTP library would freeze the event loop
  during email sending. aiosmtplib solves this by using asyncio-native SMTP.

Configuration (add to .env):
    gmail_user=your_gmail@gmail.com
    gmail_app_password=your_16_char_app_password   ← NOT your regular Gmail password

How to get a Gmail App Password:
    1. Enable 2-Step Verification on your Google account
    2. Go to: Google Account → Security → App Passwords
    3. Generate a password for "Mail" on "Other device"
    4. Paste that 16-char password as gmail_app_password
"""

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from dotenv import load_dotenv

from core import logger

load_dotenv()

logging = logger(__name__)


async def send_email(subject: str, to_email: str, text: str, html: str) -> bool:
    """
    Send an email asynchronously via Gmail SMTP (TLS on port 587).

    Args:
        subject: Email subject line
        to_email: Recipient email address
        text: Plain-text fallback body (for email clients that don't render HTML)
        html: HTML body (shown by default in modern email clients)

    Returns:
        True if sent successfully

    Raises:
        Exception: If SMTP credentials are missing or sending fails
    """
    try:
        # Read SMTP credentials from environment variables loaded from .env.
        gmail_user = os.environ.get("gmail_user")
        gmail_app_password = os.environ.get("gmail_app_password")

        # Stop early with a clear error if the email configuration is missing.
        if not gmail_user or not gmail_app_password:
            raise ValueError("Gmail credentials not configured in .env")

        # Create a multipart email so the client can choose either the plain-text
        # version or the HTML version depending on what it supports.
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = gmail_user
        message["To"] = to_email

        # Attach both formats to the same email message.
        message.attach(MIMEText(text, "plain"))
        message.attach(MIMEText(html, "html"))

        # Send the email using Gmail's SMTP server with STARTTLS encryption.
        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=gmail_user,
            password=gmail_app_password,
        )

        logging.info(f"Email sent to {to_email} | subject: {subject}")
        return True

    except Exception as error:
        logging.error(f"send_email failed for {to_email}: {error}")
        raise
