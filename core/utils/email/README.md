# Email Utils

This folder contains the email-related helper code used by the tutorial.

Files in this folder:

- `email_helper.py`: sends email through Gmail SMTP using `aiosmtplib`
- `email_template_generator.py`: builds the plain-text and HTML content for emails

How the flow works:

1. Controller decides an email should be sent
2. Template generator builds the subject, text, and HTML
3. Email helper sends the email using SMTP credentials from `.env`

Beginner note:

- Splitting sending logic and template logic makes the code easier to test and reuse
