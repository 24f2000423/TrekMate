from celery import Celery
from celery.schedules import crontab
from config import Config

def make_celery(app_name=__name__):
    celery = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['tasks']
    )
    celery.conf.update(
        timezone=Config.CELERY_TIMEZONE,
        enable_utc=True,
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        beat_schedule={
            'send-daily-trek-reminders': {
                'task': 'tasks.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),  # Daily at 8:00 AM
            },
            'generate-monthly-activity-report': {
                'task': 'tasks.generate_monthly_activity_report',
                'schedule': crontab(day_of_month='1', hour=0, minute=0),  # 1st of every month
            },
        }
    )
    return celery

celery_app = make_celery('trekking_management_celery')
