from parameterized import parameterized
from rest_framework import status
from rest_framework.authtoken.models import Token

from authentication.models import User
from notifications.base_test import BaseTestCase


class RegistrationViewTest(BaseTestCase):

    def test_registration_with_valid_creds_success(self):
        email = 'q@q.com'
        password = 'UserPassword'
        self.client.credentials()
        response = self.client.post('/auth/sign_up/', data={'email': email, 'password': password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get('token', None))

    @parameterized.expand([
        ('Invalid email', 'q@.com', 'Password'),
        ('Invalid email', '@.com', 'Password'),
        ('Invalid email', 'qcom', 'Password'),
        ('Invalid email', 'q q.com', 'Password'),
        ('Invalid password', 'q@q.com', ''),
    ])
    def test_registration_with_invalid_creds_failure(self, _, email, password):
        self.client.credentials()
        response = self.client.post('/auth/sign_up/', data={'email': email, 'password': password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_with_creds_of_existing_user_failure(self):
        user, password = self._create_stub_user()
        self.client.credentials()
        response = self.client.post('/auth/sign_up/', data={'email': user.email, 'password': password},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPIViewTest(BaseTestCase):

    def test_user_login_with_valid_creds_success(self):
        user, password = self._create_stub_user()
        self.client.credentials()
        response = self.client.post('/auth/log_in/', data={'email': user.email, 'password': password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], Token.objects.get(user=user).key)

    def test_missed_user_login_failure(self):
        email = 'q@q.com'
        password = 'HereMustBeAPassword'
        self.client.credentials()
        response = self.client.post('/auth/log_in/', data={'email': email, 'password': password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileAPIViewTest(BaseTestCase):

    def test_authenticated_client_profile_receiving_success(self):
        pk = self.client_user.pk
        email = self.client_user.email
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pk'], pk)
        self.assertEqual(response.data['email'], email)

    def test_unauthenticated_client_profile_receiving_failure(self):
        self.client.credentials()
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AllUsersAPIView(BaseTestCase):

    def test_users_content_for_authorized_user_success(self):
        users_emails = (
            'q@q.com',
            'qw@q.com',
            'qe@q.com',
            'qr@q.com',
            'qt@q.com',
        )
        for email in users_emails:
            self._create_stub_user(email=email)
        users_data = list(User.objects.all().values('pk', 'email'))
        response = self.client.get('/auth/all_users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(users_data))
        for response_user_data in response.data:
            self.assertIn(response_user_data, users_data)

    def test_users_content_for_unauthorized_user_failure(self):
        self.client.credentials()
        response = self.client.get('/auth/all_users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
