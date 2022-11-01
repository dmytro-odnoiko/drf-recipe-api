from datetime import datetime, timedelta

from core.utils import send_emails

from celery import shared_task

@shared_task()
def send_registered_emails(emails, info=None):
    send_emails(emails, info)

@shared_task(bind=True, name='send_email_last_login_count')
def send_email_last_login_count(self):
    from users.models import User

    login_count = User.objects.filter(
        last_login__range=[datetime.now() - timedelta(days=1), datetime.now()]
    ).count()

    info = {
        'subject': 'Logins for last day',
        'message': f'There were {login_count} logins for last 24 hours.'
    }

    emails = []
    for user in User.objects.filter(is_superuser=True).all():
        emails.append(user.email)
    
    send_emails(emails, info)

@shared_task(bind=True, name='periodic_print')
def periodic_print(self):
    try:
        if datetime.now().hour % 2 == 1:
            raise Exception
        print(datetime.now())
    except Exception as e:
        self.retry(countdown=600)