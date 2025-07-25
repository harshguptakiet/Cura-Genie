# Mock email sender utility

def send_email(to_email, subject, body):
    print(f"Sending email to {to_email}: {subject}\n{body}")
    # In production, use Flask-Mail, SendGrid, AWS SES, etc.
    return True
