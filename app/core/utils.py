import uuid
import os

from django.core.mail import send_mail
from django.conf import settings


def image_filepath(instance, filename):
    """Generate filepath for image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', repr(instance), filename)


def send_emails(emails, info=None):
    if info:
        subject = info.get('subject')
        message = info.get('message')
    else:
        subject = 'Thank you for registering to our site'
        message = ' it  means a world to us.'
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, emails)