from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Category, Product
from orders.models import Order, OrderItem
from .models import Review

User = get_user_model()


class ReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='pass123')
        self.other_user = User.objects.create_user(username='reviewer2', password='pass123')
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            category=self.category, name='Keyboard', slug='keyboard',
            price='40.00', stock=10
        )
        self.client.force_authenticate(user=self.user)

    def test_cannot_review_unpurchased_product(self):
        url = reverse('review-list')
        response = self.client.post(url, {'product': self.product.id, 'rating': 5, 'comment': 'Nice'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_review_purchased_product(self):
        order = Order.objects.create(user=self.user, total_price='40.00', status='completed')
        OrderItem.objects.create(
            order=order, product=self.product, product_name=self.product.name,
            price=self.product.price, quantity=1
        )
        url = reverse('review-list')
        response = self.client.post(url, {'product': self.product.id, 'rating': 5, 'comment': 'Nice'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_review_same_product_twice(self):
        order = Order.objects.create(user=self.user, total_price='40.00', status='completed')
        OrderItem.objects.create(
            order=order, product=self.product, product_name=self.product.name,
            price=self.product.price, quantity=1
        )
        url = reverse('review-list')
        self.client.post(url, {'product': self.product.id, 'rating': 5, 'comment': 'Nice'})
        response = self.client.post(url, {'product': self.product.id, 'rating': 4, 'comment': 'Again'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_out_of_range_rejected(self):
        order = Order.objects.create(user=self.user, total_price='40.00', status='completed')
        OrderItem.objects.create(
            order=order, product=self.product, product_name=self.product.name,
            price=self.product.price, quantity=1
        )
        url = reverse('review-list')
        response = self.client.post(url, {'product': self.product.id, 'rating': 6, 'comment': 'Bad'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_edit_others_review(self):
        order = Order.objects.create(user=self.user, total_price='40.00', status='completed')
        OrderItem.objects.create(
            order=order, product=self.product, product_name=self.product.name,
            price=self.product.price, quantity=1
        )
        review = Review.objects.create(user=self.user, product=self.product, rating=5, comment='Nice')

        self.client.force_authenticate(user=self.other_user)
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.patch(url, {'rating': 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)