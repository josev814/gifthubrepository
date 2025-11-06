import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@example.com')

def send_email_sync(to_email: str, subject: str, body: str):
    if not SENDGRID_API_KEY:
        print('SendGrid not configured, skipping', to_email)
        return {'status':'skipped'}
    message = Mail(from_email=FROM_EMAIL, to_emails=to_email, subject=subject, html_content=body)
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    resp = sg.send(message)
    return {'status':'sent', 'code': resp.status_code}
