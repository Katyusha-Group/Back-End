import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.conf.enable_utc = False


app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()



@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    #print("setup_periodic_tasks")
    sender.add_periodic_task(10.0, print.s('Hello World'), name='add every 10')
