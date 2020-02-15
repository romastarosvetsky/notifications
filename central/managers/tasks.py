from celery.signals import worker_ready

from central.managers.notifier import Notifier
from notifications import celery_app


@worker_ready.connect
def configure_existing_notifications(sender, *args, **kwargs):
    with sender.app.connection() as connection:
        sender.app.send_task('central.managers.tasks.create_notification_tasks_on_startup', *args,
                             connection=connection)


@celery_app.task
def send_notification(notification_id):
    Notifier().send_notification(notification_id)


@celery_app.task
def create_notification_tasks_on_startup():
    notifications = Notifier.get_not_sent_notifications()
    for pk, activation_time in notifications:
        send_notification.apply_async(args=[pk], eta=activation_time)

