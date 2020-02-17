from copy import deepcopy
from datetime import timedelta
from unittest import mock

from django.utils import timezone
from rest_framework import status

from central.models import Notification
from notifications.base_test import BaseTestCase


class NotificationViewSetTest(BaseTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.send_task = mock.patch('central.managers.tasks.send_notification', new=mock.MagicMock())
        self.send_task.start()

    DEFAULT_NOTIFICATION_FIXTURE = {
        "title": "Title",
        "description": "Description",
        "place": "SRID=4326;POINT (24.91015539184849 29.40029149419285)",
        "participants": [
            {"pk": 1}
        ],
        "activation_time": str(timezone.now() + timedelta(days=1)),
        "sent": False
    }

    def _create_default_empty_notification(self, owner=None, activation_time=None, **kwargs):
        return Notification.objects.create(owner=owner or self.client_user,
                                           activation_time=activation_time or timezone.now(), **kwargs)

    def test_create_notification_with_authenticated_user_success(self):
        response = self.client.post('/central/notifications/', data=self.DEFAULT_NOTIFICATION_FIXTURE, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_notification_with_unauthenticated_user_failure(self):
        self.client.credentials()
        response = self.client.post('/central/notifications/', data=self.DEFAULT_NOTIFICATION_FIXTURE, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_notification_with_owner_user_success(self):
        notification = self._create_default_empty_notification()
        response = self.client.put('/central/notifications/{pk}/'.format(pk=notification.pk),
                                   data=self.DEFAULT_NOTIFICATION_FIXTURE, format='json')
        notification.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], notification.pk)
        self.assertEqual(response.data['title'], notification.title)

    def test_update_notification_with_not_authenticated_user_failure(self):
        self.client.credentials()
        notification = self._create_default_empty_notification()
        response = self.client.put('/central/notifications/{pk}/'.format(pk=notification.pk),
                                   data=self.DEFAULT_NOTIFICATION_FIXTURE, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_notification_with_not_owner_user_failure(self):
        owner, _ = self._create_stub_user()
        notification = self._create_default_empty_notification(owner=owner)
        response = self.client.put('/central/notifications/{pk}/'.format(pk=notification.pk),
                                   data=self.DEFAULT_NOTIFICATION_FIXTURE, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_notification_with_owner_user_success(self):
        notification_id = self._create_default_empty_notification().pk
        response = self.client.delete('/central/notifications/{pk}/'.format(pk=notification_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Notification.objects.filter(pk=notification_id).exists())

    def test_delete_notification_with_not_authenticated_user_failure(self):
        self.client.credentials()
        notification = self._create_default_empty_notification()
        response = self.client.delete('/central/notifications/{pk}/'.format(pk=notification.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_notification_with_not_owner_user_failure(self):
        owner, _ = self._create_stub_user()
        notification = self._create_default_empty_notification(owner=owner)
        response = self.client.delete('/central/notifications/{pk}/'.format(pk=notification.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_participated_and_owned_notifications_with_authenticated_user_success(self):
        owner, _ = self._create_stub_user()
        notification1 = self._create_default_empty_notification(owner=owner)
        notification1.participants.add(self.client_user)
        notification2 = self._create_default_empty_notification(owner=self.client_user)
        notification3 = self._create_default_empty_notification(owner=owner)
        response = self.client.get('/central/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_notifications_ids = [notification['pk'] for notification in response.data]
        self.assertListEqual(sorted(response_notifications_ids), sorted([notification1.pk, notification2.pk]))
        self.assertNotIn(notification3.pk, response_notifications_ids)

    def test_get_all_notifications_with_unauthenticated_user_failure(self):
        self.client.credentials()
        response = self.client.get('/central/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_task_for_notification_later_time_created_success(self):
        activation_time = timezone.now() + timedelta(days=1)
        fixture = deepcopy(self.DEFAULT_NOTIFICATION_FIXTURE)
        fixture['activation_time'] = str(activation_time)
        response = self.client.post('/central/notifications/', data=fixture, format='json')
        self.send_task.new.apply_async.assert_called_with(
            args=[response.data['pk'], activation_time],
            eta=activation_time
        )

    def test_send_task_for_notification_earlier_time_created_failure(self):
        activation_time = timezone.now() - timedelta(days=1)
        fixture = deepcopy(self.DEFAULT_NOTIFICATION_FIXTURE)
        fixture['activation_time'] = str(activation_time)
        self.client.post('/central/notifications/', data=fixture, format='json')
        self.send_task.new.apply_async.assert_not_called()
