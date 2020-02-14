from rest_framework import serializers

from authentication.models import User
from authentication.serializers import UserSerializer
from central.models import Notification


class ParticipantSerializer(serializers.Serializer):

    pk = serializers.IntegerField()
    email = serializers.EmailField(read_only=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class NotificationSerializer(serializers.ModelSerializer):

    owner = UserSerializer(read_only=True)
    participants = ParticipantSerializer(many=True)

    class Meta:
        model = Notification
        fields = ['pk', 'owner', 'title', 'description', 'place',
                  'participants', 'created_at', 'activation_time', 'sent']

    def create(self, validated_data):
        owner = self.context['request'].user
        participants_pk = validated_data.pop('participants')
        notification = Notification(**validated_data, owner=owner)
        notification.save()
        participants = User.objects.filter(pk__in=[d['pk'] for d in participants_pk])
        notification.participants.add(*participants)
        return notification

    def update(self, instance, validated_data):
        participants_pk = validated_data.pop('participants')
        notification_qs = Notification.objects.filter(pk=instance.pk)
        participants = User.objects.filter(pk__in=[d['pk'] for d in participants_pk])
        notification_qs.update(**validated_data)
        notification = notification_qs.first()
        notification.participants.clear()
        notification.participants.add(*participants)
        return notification
