import os

def custom_message(event, context):
    print(event)
    trigger = event.get("triggerSource")

    if trigger == "CustomMessage_SignUp" or trigger == "CustomMessage_ResendCode": # Not sure of resend would work (it's not implemented)
        username = event["userName"]
        code = event["request"]["codeParameter"]
        event["response"]["emailSubject"] = "Verify Your TrailPlanner Account"
        event["response"]["emailMessage"] = get_sign_up_message(username, code)

    if trigger == "CustomMessage_ForgotPassword":
        pass

    print(event["response"])

    return event

def get_sign_up_message(username, code):
    return f"""
        <html>
            <body style="font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;">
                <div style="max-width:500px; margin:0 auto; background:#ffffff; border:1px solid #e5e5e5; border-radius:15px; padding:24px;">
                    <h2 style="margin:0 0 10px 0;">Welcome to TrailPlanner!</h2>
                    <p style="color:#444444; font-size:14px;">
                        Hello {username}, to verify your email address please use the following code:
                    </p>
                    <div style="
                        margin:20px 0;
                        padding:4px;
                        text-align:center;
                        font-size:28px;
                        letter-spacing:5px;
                        font-weight:700;
                        background:#dfd858;
                        border:1px dashed #d4d4d8;
                        border-radius:10px;
                    ">
                        {code}
                    </div>
                    <p style="font-size:13px; color:#666666; line-height:1.5;">
                        Dont share this code with anyone. This code will expire in 24 hours.
                    </p>
                    <hr style="border:none; border-top:1px solid #eee; margin:20px 0;" />
                    <p style="font-size:12px; color:#888888; margin:0">
                        If you didn't request this email, you can safely ignore it.
                    </p>
                </div>
            </body>
        </html>
    """