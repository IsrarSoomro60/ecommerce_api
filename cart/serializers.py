from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    item_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'price', 'quantity', 'item_total')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('user',)

    def get_total_price(self, obj):
        return sum(item.item_total for item in obj.items.all())


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Product not found or inactive.")
        return value
