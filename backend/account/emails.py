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

    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email for YourApp</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
            background-color: #f8f9fa; /* Lighter, neutral background */
            color: #343a40; /* Darker text for better contrast */
            padding: 20px;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        .container {{
            max-width: 580px; /* Slightly narrower for mobile-first feel */
            margin: 40px auto;
            background: #ffffff;
            border-radius: 12px; /* More prominent rounding */
            box-shadow: 0 8px 20px rgba(0,0,0,0.08); /* Softer, deeper shadow */
            padding: 40px; /* Increased padding */
            text-align: center;
            border-top: 6px solid #007bff; /* Stronger accent border */
        }}
        h1 {{
            color: #007bff;
            font-size: 32px; /* Larger, more impactful heading */
            margin-bottom: 25px;
            font-weight: 700; /* Bolder */
        }}
        p {{
            font-size: 17px; /* Slightly larger body text */
            color: #495057;
            margin-bottom: 20px;
        }}
        .code-box {{
            margin: 35px auto; /* More vertical space */
            padding: 22px 30px;
            font-size: 38px; /* Significantly larger code */
            letter-spacing: 12px; /* More pronounced spacing */
            font-weight: bold;
            background-color: #e9f0ff; /* Lighter blue background */
            border: 2px dashed #007bff; /* Matching border color */
            border-radius: 10px;
            display: inline-block;
            user-select: all;
            color: #0056b3; /* Darker blue for code */
            cursor: text; /* Hint for users that they can select/copy */
        }}
        .expiration-note {{
            font-size: 15px;
            color: #dc3545; /* Red for urgency */
            font-weight: 600; /* Semi-bold */
            margin-top: -15px; /* Closer to code box */
            margin-bottom: 30px; /* More space before next paragraph */
        }}
        .ignore-note {{
            font-size: 14px;
            color: #6c757d; /* Slightly muted gray */
            margin-top: 30px;
        }}
        .footer {{
            margin-top: 50px; /* More space above footer */
            font-size: 14px;
            color: #adb5bd; /* Lighter gray for footer */
            border-top: 1px solid #e9ecef; /* Subtle separator */
            padding-top: 25px;
        }}
        .greeting-name {{
            font-weight: bold; /* Bold the email address */
            color: #007bff; /* Make the email address stand out */
        }}
    </style>
    </head>
    <body>
    <div class="container">
        <h1>Welcome to YourHostelApp! 🎉</h1>
        <p>Hi <span class="greeting-name">{user.email}</span>,</p>
        <p>Thank you for registering with YourHostelApp. To complete your account setup and start exploring, please use the following verification code:</p>
        <div class="code-box">{verification_code}</div>
        <p class="expiration-note">This code will expire in <strong>15 minutes</strong>. Please enter it promptly to verify your account.</p>
        <p class="ignore-note">If you did not sign up for YourHostelApp, you can safely ignore this email.</p>
        <p class="footer">Best regards,<br>The YourHostelApp Team 🚀</p>
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
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Your Password for {app_name}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
                background-color: #f8f9fa; /* Lighter, neutral background */
                color: #343a40; /* Darker text for better contrast */
                padding: 20px;
                line-height: 1.6;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}
            .container {{
                max-width: 580px; /* Consistent width */
                margin: 40px auto;
                background: #ffffff;
                border-radius: 12px; /* Prominent rounding */
                box-shadow: 0 8px 20px rgba(0,0,0,0.08); /* Softer, deeper shadow */
                padding: 40px; /* Increased padding */
                text-align: center;
                border-top: 6px solid #ffc107; /* Orange/warning color for password reset */
            }}
            h1 {{
                color: #007bff; /* Primary blue for main heading */
                font-size: 30px; /* Slightly larger heading */
                margin-bottom: 25px;
                font-weight: 700;
            }}
            h2 {{
                color: #ffc107; /* Orange for sub-heading */
                font-size: 24px;
                margin-top: 30px;
                margin-bottom: 20px;
                font-weight: 600;
            }}
            p {{
                font-size: 17px;
                color: #495057;
                margin-bottom: 20px;
            }}
            .button-link {{
                display: inline-block;
                background-color: #007bff; /* Primary blue for button */
                color: #ffffff !important; /* Important for white text */
                padding: 14px 30px; /* Larger padding for button */
                border-radius: 8px; /* Slightly more rounded button */
                text-decoration: none;
                font-weight: bold;
                font-size: 18px; /* Larger button text */
                margin: 25px 0; /* More vertical space around button */
                box-shadow: 0 4px 10px rgba(0,123,255,0.3); /* Stronger button shadow */
                transition: background-color 0.3s ease;
            }}
            .button-link:hover {{
                background-color: #0056b3; /* Darker blue on hover */
            }}
            .link-text {{
                word-break: break-all; /* Ensures long links wrap */
                font-size: 14px;
                color: #007bff;
                text-decoration: underline;
            }}
            .security-note {{
                font-size: 15px;
                color: #dc3545; /* Red for security warning */
                font-weight: 600;
                margin-top: 30px;
            }}
            .footer {{
                margin-top: 50px;
                font-size: 14px;
                color: #adb5bd;
                border-top: 1px solid #e9ecef;
                padding-top: 25px;
            }}
            .greeting-name {{
                font-weight: bold;
                color: #007bff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Password Reset for {app_name}</h1>
            <p>Hi <span class="greeting-name">{user.email}</span>,</p>
            <p>You recently requested to reset your password. Please click the button below to set a new one:</p>

            <a href="{reset_link}" class="button-link">Reset My Password</a>

            <p>If the button above isn't working, you can copy and paste the following link into your browser:</p>
            <p><span class="link-text">{reset_link}</span></p>

            <p class="security-note">For your security, this link is only valid for a limited time and can only be used once.</p>

            <p>If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
            
            <p class="footer">Best regards,<br>The {app_name} Team 🔒</p>
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