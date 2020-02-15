from django.conf import settings
from django.utils import timezone

from central.email.email_manager import Email
from central.models import Notification


class Notifier:

    @staticmethod
    def get_not_sent_notifications():
        return Notification.objects.filter(sent=False, activation_time__gte=timezone.now()).\
            values_list('pk', 'activation_time')

    def send_notification(self, notification_id):
        notification_qs = Notification.objects.filter(pk=notification_id).prefetch_related('participants').\
            select_related('owner')
        notification = notification_qs.first()
        participants_emails_qs = notification.participants.all().values_list('email', flat=True)
        email = Email(subject=notification.title, from_email=settings.EMAIL_HOST_USER, to=list(participants_emails_qs),
                      email_body_context={
                          'message': notification.description,
                          'owner': notification.owner.email,
                          'place': notification.place.coords,
                          'created_at': notification.created_at,
                          'activation_time': notification.activation_time
                      })
        email.send()
        notification_qs.update(sent=True)
