from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response(
                {'success': False, 'message': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check stock availability BEFORE creating anything
        for item in cart_items:
            if item.quantity > item.product.stock:
                return Response(
                    {
                        'success': False,
                        'message': f'Insufficient stock for {item.product.name}'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            total_price = sum(item.item_total for item in cart_items)

            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='pending'
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.price,
                    quantity=item.quantity
                )
                # Reduce stock
                item.product.stock -= item.quantity
                item.product.save()

            # Clear the cart
            cart_items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)