# news/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from .services import send_weekly_digest


def start_scheduler():
    """Запуск планировщика задач"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Еженедельная рассылка по понедельникам в 9:00
    scheduler.add_job(
        send_weekly_digest,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        id="weekly_digest",
        max_instances=1,
        replace_existing=True,
    )

    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()


# Декоратор для закрытия соединения с БД после выполнения задачи
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """Удаление старых записей о выполнении задач"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)