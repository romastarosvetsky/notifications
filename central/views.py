from django.db.models import Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from central.models import Notification
from central.permissions import NotificationOwnerManageOrReadOnly
from central.serializers import NotificationSerializer

from central.managers import tasks


class NotificationViewSet(ModelViewSet):

    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated, NotificationOwnerManageOrReadOnly, ]

    def filter_queryset(self, queryset):
        current_user = self.request.user
        return self.get_queryset().filter(Q(owner=current_user) | Q(participants=current_user)).distinct()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        self._create_task(response.data['pk'])
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        self._create_task(response.data['pk'])
        return response

    @staticmethod
    def _create_task(notification_id):
        notification = Notification.objects.filter(pk=notification_id).values('pk', 'activation_time', 'sent').first()
        if notification is not None and notification['activation_time'] >= timezone.now() and not notification['sent']:
            tasks.send_notification.apply_async(args=[notification['pk'], notification['activation_time']],
                                                eta=notification['activation_time'])
