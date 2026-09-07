from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterTests(APITestCase):
    def test_register_success(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'phone_number': '03001234567'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_defaults_to_customer_role(self):
        url = reverse('register')
        data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'testpass123',
        }
        self.client.post(url, data)
        user = User.objects.get(username='testuser2')
        self.assertEqual(user.role, 'customer')

    def test_register_missing_password_fails(self):
        url = reverse('register')
        data = {'username': 'testuser3', 'email': 'test3@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='loginuser', password='testpass123')

    def test_login_success_returns_tokens(self):
        url = reverse('login')
        response = self.client.post(url, {'username': 'loginuser', 'password': 'testpass123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password_fails(self):
        url = reverse('login')
        response = self.client.post(url, {'username': 'loginuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='meuser', password='testpass123')

    def test_me_requires_authentication(self):
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_own_data_when_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'meuser')