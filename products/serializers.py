from rest_framework import serializers
from .models import Category, Product
from decimal import Decimal

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock= serializers.IntegerField(required=True, min_value=0)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))


    class Meta:
        model = Product
        fields = (
            'id', 'category', 'category_name', 'name', 'slug',
            'description', 'price', 'stock', 'is_active',
            'created_at', 'updated_at'
        )