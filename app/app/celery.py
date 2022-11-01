import os


from celery import Celery

from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
app = Celery("app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5,
          retry_kwargs={'max_retries':3})
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

