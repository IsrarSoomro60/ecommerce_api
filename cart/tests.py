from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Category, Product
from .models import Cart, CartItem

User = get_user_model()


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cartuser', password='pass123')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            category=self.category, name='Headphones', slug='headphones',
            price='50.00', stock=20
        )
        self.client.force_authenticate(user=self.user)

    def test_get_cart_creates_empty_cart(self):
        url = reverse('cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Cart.objects.filter(user=self.user).exists())

    def test_add_to_cart(self):
        url = reverse('cart-add')
        response = self.client.post(url, {'product_id': self.product.id, 'quantity': 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_add_same_product_twice_increments_quantity(self):
        url = reverse('cart-add')
        self.client.post(url, {'product_id': self.product.id, 'quantity': 2})
        self.client.post(url, {'product_id': self.product.id, 'quantity': 3})
        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 5)

    def test_add_inactive_product_rejected(self):
        self.product.is_active = False
        self.product.save()
        url = reverse('cart-add')
        response = self.client.post(url, {'product_id': self.product.id, 'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_access_another_users_cart_item(self):
        other_user = User.objects.create_user(username='other', password='pass123')
        other_cart = Cart.objects.create(user=other_user)
        other_item = CartItem.objects.create(cart=other_cart, product=self.product, quantity=1)

        url = reverse('cart-item-update', kwargs={'item_id': other_item.id})
        response = self.client.patch(url, {'quantity': 5})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)