from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Category, Product
from cart.models import Cart, CartItem
from .models import Order

User = get_user_model()


class CheckoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', password='pass123')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            category=self.category, name='Mouse', slug='mouse',
            price='25.00', stock=10
        )
        self.client.force_authenticate(user=self.user)

    def test_checkout_empty_cart_fails(self):
        url = reverse('checkout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_checkout_reduces_stock_and_clears_cart(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)

        url = reverse('checkout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)
        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 0)

    def test_checkout_insufficient_stock_fails(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=999)

        url = reverse('checkout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)  # unchanged


class OrderStatusTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='cust1', password='pass123', role='customer')
        self.admin = User.objects.create_user(username='admin3', password='pass123', role='admin')
        self.category = Category.objects.create(name='Books', slug='books')
        self.product = Product.objects.create(
            category=self.category, name='Novel', slug='novel',
            price='15.00', stock=5
        )
        self.order = Order.objects.create(user=self.customer, total_price='15.00', status='pending')

    def test_customer_can_cancel_own_pending_order(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-status-update', kwargs={'pk': self.order.id})
        response = self.client.patch(url, {'status': 'cancelled'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_mark_order_completed(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-status-update', kwargs={'pk': self.order.id})
        response = self.client.patch(url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_mark_order_completed(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('order-status-update', kwargs={'pk': self.order.id})
        response = self.client.patch(url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_cancel_others_order(self):
        other_customer = User.objects.create_user(username='cust2', password='pass123')
        self.client.force_authenticate(user=other_customer)
        url = reverse('order-status-update', kwargs={'pk': self.order.id})
        response = self.client.patch(url, {'status': 'cancelled'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_sees_all_orders_customer_sees_own(self):
        Order.objects.create(user=self.admin, total_price='30.00', status='pending')

        self.client.force_authenticate(user=self.customer)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(len(response.data['data']), 1)

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('order-list'))
        self.assertEqual(len(response.data['data']), 2)