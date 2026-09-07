from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Category, Product

User = get_user_model()


class ProductPermissionTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='cust', password='pass123', role='customer')
        self.admin = User.objects.create_user(username='admin1', password='pass123', role='admin')
        self.category = Category.objects.create(name='Electronics', slug='electronics')

    def test_anyone_can_list_products(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_create_product(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-list')
        data = {
            'category': self.category.id, 'name': 'Phone', 'slug': 'phone',
            'price': '100.00', 'stock': 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_product(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('product-list')
        data = {
            'category': self.category.id, 'name': 'Phone', 'slug': 'phone',
            'price': '100.00', 'stock': 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_cannot_create_product(self):
        url = reverse('product-list')
        data = {
            'category': self.category.id, 'name': 'Phone', 'slug': 'phone',
            'price': '100.00', 'stock': 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductValidationTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin2', password='pass123', role='admin')
        self.category = Category.objects.create(name='Books', slug='books')
        self.client.force_authenticate(user=self.admin)

    def test_negative_price_rejected(self):
        url = reverse('product-list')
        data = {
            'category': self.category.id, 'name': 'Book', 'slug': 'book',
            'price': '-5.00', 'stock': 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_price_rejected(self):
        url = reverse('product-list')
        data = {
            'category': self.category.id, 'name': 'Book', 'slug': 'book2',
            'price': '0', 'stock': 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_stock_rejected(self):
        url = reverse('product-list')
        data = {
            'category': self.category.id, 'name': 'Book', 'slug': 'book3',
            'price': '10.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)