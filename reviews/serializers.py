from rest_framework import serializers
from .models import Review
from orders.models import OrderItem


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = ('id', 'product', 'username', 'rating', 'comment', 'created_at', 'updated_at')
        read_only_fields = ('user',)


    def validate(self, data):
        request = self.context['request']
        product = data.get('product')

        # Only for creation, not update
        if self.instance is None:
            has_purchased = OrderItem.objects.filter(
                order__user=request.user,
                product=product
            ).exists()

            if not has_purchased:
                raise serializers.ValidationError(
                    "You can only review products you have purchased."
                )

            if Review.objects.filter(user=request.user, product=product).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this product."
                )

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)