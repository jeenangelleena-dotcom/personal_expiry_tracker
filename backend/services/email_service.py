import smtplib
from email.message import EmailMessage
from flask import current_app


def send_email(to_email, subject, message):
    """
    Send a plain-text email.
    """

    mail_server = current_app.config.get("MAIL_SERVER")
    mail_port = current_app.config.get("MAIL_PORT")
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")

    if not mail_server:
        raise ValueError("MAIL_SERVER is not configured.")

    if not mail_username:
        raise ValueError("MAIL_USERNAME is not configured.")

    if not mail_password:
        raise ValueError("MAIL_PASSWORD is not configured.")

    email = EmailMessage()

    email["From"] = mail_username
    email["To"] = to_email
    email["Subject"] = subject

    email.set_content(message)

    with smtplib.SMTP(mail_server, mail_port) as smtp:

        smtp.starttls()

        smtp.login(
            mail_username,
            mail_password
        )

        smtp.send_message(email)


def send_expiry_reminder(
    to_email,
    object_name,
    days_remaining,
    reminder_level
):
    """
    Send a styled expiry reminder email.
    """

    if reminder_level == "Upcoming":

        subject = f"Upcoming Expiry: {object_name}"

        title = "Your item is approaching expiry"

        status_text = "30 days remaining"

        status_class = "upcoming"

        message = (
            f"{object_name} will expire in 30 days. "
            "Please keep this item in mind."
        )

    elif reminder_level == "Urgent":

        subject = f"Urgent Expiry Reminder: {object_name}"

        title = "Your item is expiring soon"

        status_text = "7 days remaining"

        status_class = "urgent"

        message = (
            f"{object_name} will expire in 7 days. "
            "Please take the necessary action soon."
        )

    elif reminder_level == "Expires Today":

        subject = f"Expires Today: {object_name}"

        title = "Your item expires today"

        status_text = "Expires today"

        status_class = "today"

        message = (
            f"{object_name} expires today. "
            "Please check this item immediately."
        )

    else:

        subject = f"Expiry Reminder: {object_name}"

        title = "Expiry reminder"

        status_text = (
            f"{days_remaining} days remaining"
        )

        status_class = "default"

        message = (
            f"{object_name} has "
            f"{days_remaining} days remaining."
        )


    html_content = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>Expiry Tracker Reminder</title>

</head>


<body style="
    margin:0;
    padding:0;
    background:#f3f6fb;
    font-family:Arial,Helvetica,sans-serif;
">

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="
        background:#f3f6fb;
        padding:35px 15px;
    "
>

<tr>

<td align="center">

<table
    width="600"
    cellpadding="0"
    cellspacing="0"
    style="
        max-width:600px;
        width:100%;
        background:#ffffff;
        border-radius:18px;
        overflow:hidden;
        box-shadow:0 8px 30px rgba(24,42,70,0.12);
    "
>


<!-- HEADER -->

<tr>

<td style="
    background:#24449a;
    padding:28px 30px;
    text-align:center;
">

<div style="
    font-size:34px;
    line-height:40px;
">
    ⏰
</div>

<div style="
    color:#ffffff;
    font-size:25px;
    font-weight:bold;
    margin-top:6px;
">
    Expiry Tracker
</div>

<div style="
    color:#dce6ff;
    font-size:13px;
    margin-top:6px;
">
    Smart expiry management
</div>

</td>

</tr>


<!-- MAIN CONTENT -->

<tr>

<td style="
    padding:35px 35px 30px;
">

<h1 style="
    margin:0 0 12px;
    color:#172033;
    font-size:24px;
">
    {title}
</h1>


<p style="
    margin:0 0 22px;
    color:#5f6b7a;
    font-size:15px;
    line-height:1.7;
">
    This is a reminder from your Personal Expiry Tracker.
    We are notifying you so you can take action before
    your stored item expires.
</p>


<!-- OBJECT CARD -->

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    style="
        border:1px solid #e1e7f0;
        border-radius:14px;
        background:#f8faff;
    "
>

<tr>

<td style="
    padding:22px;
">

<div style="
    color:#687587;
    font-size:12px;
    text-transform:uppercase;
    letter-spacing:1px;
    margin-bottom:7px;
">
    Object
</div>


<div style="
    color:#172033;
    font-size:21px;
    font-weight:bold;
    margin-bottom:18px;
">
    {object_name}
</div>


<div style="
    color:#536176;
    font-size:15px;
    line-height:1.8;
">

<strong>
Expiry Status:
</strong>

<span style="
    color:#24449a;
    font-weight:bold;
">
    {status_text}
</span>

</div>


<div style="
    color:#536176;
    font-size:15px;
    line-height:1.8;
">

<strong>
Days Remaining:
</strong>

{days_remaining}

</div>

</td>

</tr>

</table>


<!-- MESSAGE -->

<div style="
    margin-top:22px;
    padding:18px 20px;
    border-left:4px solid #5267e8;
    background:#f1f3ff;
    border-radius:8px;
    color:#39455a;
    font-size:14px;
    line-height:1.7;
">

{message}

</div>


<!-- ACTION MESSAGE -->

<p style="
    margin:24px 0 0;
    color:#536176;
    font-size:14px;
    line-height:1.7;
">

Please open your Expiry Tracker and review the
item before its expiry date.

</p>

</td>

</tr>


<!-- FOOTER -->

<tr>

<td style="
    background:#f7f9fc;
    padding:22px 30px;
    text-align:center;
    border-top:1px solid #e7ebf2;
">

<div style="
    color:#24449a;
    font-size:14px;
    font-weight:bold;
">
    Personal Expiry Tracker
</div>


<div style="
    color:#8994a4;
    font-size:12px;
    margin-top:7px;
">
    Stay organized. Never miss an expiry date.
</div>


<div style="
    color:#a0a8b5;
    font-size:11px;
    margin-top:12px;
">
    This is an automatic reminder email.
</div>

</td>

</tr>


</table>

</td>

</tr>

</table>

</body>

</html>
"""


    plain_text = f"""
EXPIRY TRACKER
==============

{title}

Object: {object_name}

Status: {status_text}

Days Remaining: {days_remaining}

{message}

Please open your Personal Expiry Tracker and review
this item before its expiry date.

This is an automatic reminder email.
"""


    mail_server = current_app.config.get("MAIL_SERVER")
    mail_port = current_app.config.get("MAIL_PORT")
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")


    if not mail_server:
        raise ValueError(
            "MAIL_SERVER is not configured."
        )

    if not mail_username:
        raise ValueError(
            "MAIL_USERNAME is not configured."
        )

    if not mail_password:
        raise ValueError(
            "MAIL_PASSWORD is not configured."
        )


    email = EmailMessage()

    email["From"] = mail_username

    # This is the registered user's email.
    email["To"] = to_email

    email["Subject"] = subject


    # Plain text fallback
    email.set_content(plain_text)


    # Styled HTML version
    email.add_alternative(
        html_content,
        subtype="html"
    )


    with smtplib.SMTP(
        mail_server,
        mail_port
    ) as smtp:

        smtp.starttls()

        smtp.login(
            mail_username,
            mail_password
        )

        smtp.send_message(email)


    return True