from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from central.models import Notification
from central.serializers import NotificationSerializer


class NotificationViewSet(ModelViewSet):

    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated, ]

    def filter_queryset(self, queryset):
        current_user = self.request.user
        return self.get_queryset().filter(Q(owner=current_user) | Q(participants=current_user))
