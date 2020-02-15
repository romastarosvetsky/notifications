from django.db.models import Q
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
        notification = Notification.objects.filter(pk=response.data['pk']).values('pk', 'activation_time').first()
        tasks.send_notification.apply_async(args=[notification['pk']], eta=notification['activation_time'])
        return response
