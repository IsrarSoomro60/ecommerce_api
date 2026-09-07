from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.responses import success_response, error_response
from rest_framework.serializers import Serializer, IntegerField
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer
from products.models import Product
from drf_spectacular.utils import extend_schema, OpenApiExample


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return success_response(data=serializer.data, message="Cart fetched successfully")


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=AddToCartSerializer)
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        product = Product.objects.get(id=serializer.validated_data['product_id'])
        quantity = serializer.validated_data['quantity']

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return success_response(message="Item added to cart", status_code=status.HTTP_201_CREATED)


class UpdateQuantitySerializer(Serializer):
    quantity = IntegerField(min_value=1)

class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UpdateQuantitySerializer)
    def patch(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return error_response(message="Cart item not found", status_code=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity')
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return error_response(message="Quantity must be a valid number", status_code=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return error_response(message="Quantity must be at least 1", status_code=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        return success_response(message="Quantity updated")


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            
        except CartItem.DoesNotExist:
            return error_response(message="Cart item not found", status_code=status.HTTP_404_NOT_FOUND)

        cart_item.delete()
        return success_response(message="Item removed from cart")