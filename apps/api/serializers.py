from rest_framework import serializers
from apps.product.models import Product
from apps.history.models import *


class ProductSerializer(serializers.ModelSerializer):
    d_sale_price = serializers
    class Meta:
        model = Product
        fields = '__all__'


class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = '__all__'

class SoldHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SoldHistory
        fields = '__all__'
