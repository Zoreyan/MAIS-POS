from rest_framework import serializers
from apps.product.models import Product



class ProductSerializer(serializers.ModelSerializer):
    d_sale_price = serializers
    class Meta:
        model = Product
        fields = '__all__'