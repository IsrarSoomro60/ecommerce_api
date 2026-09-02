from rest_framework.viewsets import ModelViewSet
from core.permissions import IsAdminOrStaffOrReadOnly
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrStaffOrReadOnly]


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrStaffOrReadOnly]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']