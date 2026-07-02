import os

LOGO_URL = os.environ.get("LOGO_URL")

def custom_message(event, context):
    print(event)
    trigger = event.get("triggerSource")
    username = event["userName"]
    code = event["request"]["codeParameter"]

    if trigger == "CustomMessage_SignUp":
        event["response"]["emailSubject"] = "Verify Your TrailCount Account"
        event["response"]["emailMessage"] = get_email_layout(username, code, "verify your email address")

    if trigger == "CustomMessage_ResendCode":
        event["response"]["emailSubject"] = "Verify Your TrailCount Account (Resend)"
        event["response"]["emailMessage"] = get_email_layout(username, code, "verify your email address")

    if trigger == "CustomMessage_ForgotPassword":
        event["response"]["emailSubject"] = "Reset Your TrailCount Account Password"
        event["response"]["emailMessage"] = get_email_layout(username, code, "reset your password")

    print(event["response"])

    return event

def get_email_layout(username, code, purpose):
    return f"""
        <html>
            <body style="font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif; background-color: #eeeeee">
                <div>
                    <div style="
                        max-width: 500px;
                        margin: 0 auto;
                        background: #ffffff;
                        border:1.75px solid #3c4c4c;
                        border-bottom: none;
                        border-radius: 15px 15px 0 0;
                        padding: 24px;
                        text-align: center;
                    ">
                        <a href="#">
                            <img 
                                src="{LOGO_URL}"
                                alt="AWALogo"
                                style="width: 70%; margin: 0px auto 20px auto;"
                            />
                        </a>
                        <h2 style="margin:0 0 10px 0;">Welcome to TrailCount!</h2>
                        <p style="color: #444444; font-size: 14px;">
                            Hello {username}, to {purpose} please use the following code:
                        </p>
                        <div style="
                            margin: 20px 0;
                            padding: 4px;
                            text-align: center;
                            font-size: 28px;
                            letter-spacing: 5px;
                            font-weight: 700;
                            background: #dfd858;
                            border: 1.75px solid #3c4c4c;
                            border-radius: 15px;
                            color: #3c4c4c;
                        ">
                            {code}
                        </div>
                        <p style="font-size: 13px; color: #666666; line-height: 1.5;">
                            Dont share this code with anyone. This code will expire in 24 hours.
                        </p>
                    </div>
                    <div style="
                        max-width: 500px;
                        margin: 0 auto;
                        background: #2b6b64;
                        border: 1.75px solid #3c4c4c;
                        border-top: none;
                        border-radius: 0 0 15px 15px;
                        padding: 24px;
                        text-align: center;
                        color: #ffffff;
                        font-size: 12px;
                    ">
                        <p style="margin: 0 0 20px 0;">
                            If you didn't request this email, you can safely ignore it.
                        </p>
                        <p style="margin: 0">
                            Copyright 2025, Adirondack Wilderness Advocates. All rights reserved. 
                        </p>
                    </div>
                </div>
            </body>
        </html>
    """