from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def sendRegistrationMail(user):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    verification_code = user.verification_code

    subject = "Your YourApp Verification Code - Action Required!"

    text_message = f"""Hi {user.email},

    Thanks for joining YourApp! To complete your registration, please use the following verification code:

    {verification_code}

    This code is valid for 15 minutes. Please enter it promptly to verify your account.

    If you didn't sign up for YourApp, please ignore this email.

    Best regards,
    The YourApp Team
    """

    app_name = "YourHostelApp"

    html_message = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <title>Verify Your Email for {app_name}</title>
    <style>
        body {{
            background-color: #f9f9f9;
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #343a40;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            padding: 40px;
            text-align: center;
            border-top: 6px solid #007bff;
        }}
        h1 {{
            font-size: 28px;
            color: #007bff;
            margin-bottom: 20px;
            font-weight: 700;
        }}
        p {{
            font-size: 16px;
            color: #495057;
            margin-bottom: 20px;
        }}
        .greeting-name {{
            font-weight: bold;
            color: #007bff;
        }}
        .code-box {{
            margin: 30px auto;
            padding: 20px 32px;
            font-size: 34px;
            letter-spacing: 10px;
            font-weight: bold;
            background-color: #e9f0ff;
            border: 2px dashed #007bff;
            border-radius: 8px;
            display: inline-block;
            color: #0056b3;
            user-select: text;
            -webkit-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
        }}
        .hint {{
            font-size: 14px;
            color: #6c757d;
            margin-top: 8px;
        }}
        .expiration-note {{
            font-size: 15px;
            color: #dc3545;
            font-weight: 600;
            margin-bottom: 28px;
        }}
        .ignore-note {{
            font-size: 14px;
            color: #6c757d;
            margin-top: 32px;
        }}
        .footer {{
            margin-top: 50px;
            font-size: 14px;
            color: #adb5bd;
            border-top: 1px solid #e9ecef;
            padding-top: 25px;
        }}
    </style>
    </head>
    <body>
    <div class="container">
        <h1>Welcome to {app_name} </h1>
        <p>Hi <span class="greeting-name">{user.email}</span>,</p>
        <p>Thank you for registering with {app_name}. To complete your account setup, use the verification code below:</p>
        
        <div class="code-box">{verification_code}</div>
        <div class="hint">Long press or select the above code to copy it.</div>

        <!-- Plain text version for easy copy-paste -->
        <p style="font-size: 16px; margin-top: 30px;">
            Or just copy this code manually:<br>
            <code style="font-family: monospace; font-size: 20px; background-color: #f1f1f1; padding: 8px 12px; border-radius: 5px; display: inline-block; color: #000;">
                {verification_code}
            </code>
        </p>

        <p class="expiration-note">This code will expire in <strong>15 minutes</strong>.</p>
        <p class="ignore-note">If you did not sign up for {app_name}, you can safely ignore this email.</p>
        <div class="footer">
            &mdash; The {app_name} Team 🚀
        </div>
    </div>
    </body>
    </html>
    """


    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email=email_from,
        to=recipient_list
    )
    email.attach_alternative(html_message, "text/html")
    email.send()



def sendPasswordResetEmail(user , link):
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    reset_link = link
    app_name = "YourHostelApp"

    subject = f"Action Required: Reset Your {app_name} Password"

    text_message = f"""Hi {user.email},

    You recently requested to reset your password for your {app_name} account.

    Please click on the following link to reset your password:
    {reset_link}

    This link is valid for a limited time (usually 24 hours or less, depending on your token expiry).

    If you did not request a password reset, please ignore this email. Your password will remain unchanged.

    Thanks,
    The {app_name} Team
    """

    html_message = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Reset Your {app_name} Password</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                background-color: #f9f9f9;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                padding: 40px 20px;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.05);
                text-align: center;
            }}
            .logo {{
                margin-bottom: 30px;
            }}
            .logo img {{
                height: 40px;
            }}
            h1 {{
                font-size: 24px;
                margin-bottom: 20px;
                color: #000;
            }}
            p {{
                font-size: 16px;
                line-height: 1.6;
                color: #555;
            }}
            a.button {{
                display: inline-block;
                margin-top: 30px;
                background-color: #00b894;
                color: white !important;
                text-decoration: none;
                padding: 14px 24px;
                border-radius: 6px;
                font-weight: 600;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                transition: background 0.3s ease;
            }}
            a.button:hover {{
                background-color: #00997a;
            }}
            .link {{
                word-break: break-all;
                color: #00b894;
                font-size: 14px;
                margin-top: 15px;
            }}
            .footer {{
                font-size: 13px;
                color: #999;
                margin-top: 40px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <!-- Add your logo URL if available -->
                <img src="https://yourhostelweb.com/static/logo.png" alt="{app_name} Logo" />
            </div>
            <h1>Reset your {app_name} password</h1>
            <p>Hi <strong>{user.email}</strong>,</p>
            <p>You recently requested to reset your password. Click the button below to set a new one:</p>
            <a href="{reset_link}" class="button">Reset Password</a>
            <p class="link">Or paste this link into your browser:<br>{reset_link}</p>
            <p>If you did not request this, you can safely ignore this email.</p>
            <div class="footer">
                &copy; {app_name} • Secure password reset
            </div>
        </div>
    </body>
    </html>
    """

    email = EmailMultiAlternatives(
    subject=subject,
    body=text_message,
    from_email=email_from,
    to=recipient_list
    )
    email.attach_alternative(html_message, "text/html")
    email.send()