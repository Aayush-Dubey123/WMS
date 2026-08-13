"""
email_template_generator.py — HTML + plain-text email template builders.

All templates return a dict with three keys:
    {
        "subject": str,
        "text":    str,   ← plain-text fallback
        "html":    str,   ← full HTML version
    }

This keeps templates decoupled from the sending logic — email_helper.py just
receives the dict and sends it. You can swap templates without touching SMTP code.

Branding is pulled from environment variables so the same code works for any project.
"""

import os

from dotenv import load_dotenv

load_dotenv()

COMPANY_NAME = os.environ.get("company_name", "MyApp")
SUPPORT_EMAIL = os.environ.get("support_email", "support@example.com")
LOGO_URL = os.environ.get("logo_url", "")


def _base_html(title: str, body_html: str) -> str:
    """
    Wrap content in a minimal, responsive HTML email shell.
    Works in Gmail, Outlook, Apple Mail, and mobile clients.
    """
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.1);">
          <!-- Header -->
          <tr>
            <td style="background:#000000;padding:24px;text-align:center;">
              {"<img src='" + LOGO_URL + "' alt='" + COMPANY_NAME + "' height='40'/>" if LOGO_URL else
               f"<span style='color:#fff;font-size:22px;font-weight:bold;'>{COMPANY_NAME}</span>"}
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px 48px;">
              {body_html}
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background:#f9f9f9;padding:20px 48px;text-align:center;
                       color:#999;font-size:12px;border-top:1px solid #eee;">
              Need help? Email us at
              <a href="mailto:{SUPPORT_EMAIL}" style="color:#000;">{SUPPORT_EMAIL}</a><br/>
              &copy; {COMPANY_NAME}. All rights reserved.
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def welcome_email_with_credentials(name: str, email: str, password: str) -> dict:
    """
    Send login credentials after auto-account creation.
    Called by UserController.create_user().

    Args:
        name: User's first name
        email: User's email address (their login username)
        password: Auto-generated plain-text password (sent only once)

    Returns:
        dict with subject, text, html keys
    """
    subject = f"Welcome to {COMPANY_NAME} — Your Login Credentials"

    body_html = f"""
      <h2 style="color:#000;margin-bottom:8px;">Welcome, {name}! 👋</h2>
      <p style="color:#444;font-size:15px;line-height:1.6;">
        Your account has been created. Here are your login credentials:
      </p>
      <table cellpadding="12" cellspacing="0" width="100%"
             style="background:#f9f9f9;border-radius:6px;margin:24px 0;font-size:15px;">
        <tr>
          <td style="color:#555;width:40%;"><strong>Email</strong></td>
          <td style="color:#000;">{email}</td>
        </tr>
        <tr>
          <td style="color:#555;"><strong>Password</strong></td>
          <td style="color:#000;letter-spacing:2px;">{password}</td>
        </tr>
      </table>
      <p style="color:#e00;font-size:13px;">
        ⚠ Please change your password after your first login.
      </p>
      <p style="color:#666;font-size:13px;margin-top:24px;">
        If you did not create this account, please contact
        <a href="mailto:{SUPPORT_EMAIL}" style="color:#000;">{SUPPORT_EMAIL}</a>.
      </p>
    """

    text = (
        f"Welcome to {COMPANY_NAME}, {name}!\n\n"
        f"Email: {email}\nPassword: {password}\n\n"
        f"Please change your password after first login.\n"
        f"Support: {SUPPORT_EMAIL}"
    )

    return {"subject": subject, "text": text, "html": _base_html(subject, body_html)}


def generate_email_template(
    name: str,
    subject: str,
    title: str,
    description: str,
    action_code: str = "",
    cta_text: str = "",
    cta_link: str = "",
) -> dict:
    """
    Generic branded email template for OTPs, notifications, etc.

    Args:
        name: Recipient's first name
        subject: Email subject line
        title: Bold heading in the email body
        description: Main paragraph / message body
        action_code: OTP or verification code (shown in a highlight box)
        cta_text: Call-to-action button label (optional)
        cta_link: CTA button URL (optional)

    Returns:
        dict with subject, text, html
    """
    code_block = ""
    if action_code:
        code_block = f"""
          <div style="text-align:center;margin:28px 0;">
            <span style="display:inline-block;background:#000;color:#fff;
                         font-size:32px;font-weight:bold;letter-spacing:8px;
                         padding:16px 32px;border-radius:6px;">
              {action_code}
            </span>
          </div>
        """

    cta_block = ""
    if cta_text and cta_link:
        cta_block = f"""
          <div style="text-align:center;margin:28px 0;">
            <a href="{cta_link}"
               style="display:inline-block;background:#000;color:#fff;
                      padding:14px 32px;border-radius:6px;text-decoration:none;
                      font-size:15px;font-weight:bold;">
              {cta_text}
            </a>
          </div>
        """

    body_html = f"""
      <h2 style="color:#000;margin-bottom:8px;">{title}</h2>
      <p style="color:#555;font-size:15px;line-height:1.6;">Hi {name},</p>
      <p style="color:#444;font-size:15px;line-height:1.6;">{description}</p>
      {code_block}
      {cta_block}
    """

    text = f"{title}\n\nHi {name},\n\n{description}"
    if action_code:
        text += f"\n\nCode: {action_code}"
    if cta_text and cta_link:
        text += f"\n\n{cta_text}: {cta_link}"

    return {"subject": subject, "text": text, "html": _base_html(subject, body_html)}
