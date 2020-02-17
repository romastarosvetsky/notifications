from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from authentication.models import User


class BaseTestCase(TestCase):

    def setUp(self) -> None:
        self.client_user = User.objects.create(email='admin@admin.com', password='123123123')
        self.client_token = Token.objects.create(user=self.client_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.client_token.key)

    @staticmethod
    def _create_stub_user(email='current_test@email.com', password='password'):
        return User.objects.create_user(email=email, password=password), password
