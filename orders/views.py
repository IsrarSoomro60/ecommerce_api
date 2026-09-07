from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from core.responses import success_response, error_response
from cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer
from rest_framework.exceptions import PermissionDenied
from .serializers import OrderStatusUpdateSerializer
from drf_spectacular.utils import extend_schema


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OrderStatusUpdateSerializer)
    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return error_response(message="Order not found", status_code=status.HTTP_404_NOT_FOUND)

        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        is_staff_or_admin = request.user.role in ['admin', 'staff']
        is_owner = order.user == request.user

        if not is_staff_or_admin and not is_owner:
            raise PermissionDenied("You do not have permission to modify this order.")

        if not is_staff_or_admin:
            # Customers can only cancel their OWN order, and only if still pending
            if new_status != 'cancelled':
                raise PermissionDenied("You can only cancel your own orders.")
            if order.status != 'pending':
                return error_response(
                    message="Only pending orders can be cancelled.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            if new_status == 'cancelled' and order.status != 'cancelled':
                # Restore stock since the order is being cancelled
                for item in order.items.all():
                    item.product.stock += item.quantity
                    item.product.save()

            order.status = new_status
            order.save()

        return success_response(
            data=OrderSerializer(order).data,
            message=f"Order status updated to {new_status}"
        )


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return error_response(message="Cart is empty", status_code=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.all()
        if not cart_items.exists():
            return error_response(message="Cart is empty", status_code=status.HTTP_400_BAD_REQUEST)

        for item in cart_items:
            if item.quantity > item.product.stock:
                return error_response(
                    message=f'Insufficient stock for {item.product.name}',
                    status_code=status.HTTP_400_BAD_REQUEST
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
                item.product.stock -= item.quantity
                item.product.save()

            cart_items.delete()

        serializer = OrderSerializer(order)
        return success_response(
            data=serializer.data,
            message="Order placed successfully",
            status_code=status.HTTP_201_CREATED
        )


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data, message="Orders fetched successfully")


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'staff']:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="Order fetched successfully")