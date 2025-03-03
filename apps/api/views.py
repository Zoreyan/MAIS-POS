from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.product.models import Product
from django.db.models import Q
from .serializers import ProductSerializer


class GetProduct(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        bar_code = request.GET.get('bar_code')
        product_id = request.GET.get('product_id')
        if bar_code:
            product = get_object_or_404(Product, bar_code=bar_code, shop=request.user.shop)  # Находим продукт по штрихкоду
        elif product_id:
            product = get_object_or_404(Product, id=product_id, shop=request.user.shop)
        else:
            return Response({'status': 'error', 'message': 'Штрихкод или ID не переданы'}, status=400)
        sale_price = product.discounted_price()
        product_data = {
            'id': product.id,  # Возвращаем ID продукта
            'name': product.name,
            'sale_price': product.sale_price,
            'd_sale_price':sale_price,
            'bar_code': product.bar_code,
            'quantity': product.quantity,
            'status': 'success'
        }
        return Response(product_data)


class GetProducts(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.GET.get('query', '').strip()
        filters = Q(shop=self.request.user.shop)

        if query:
            if query.isdigit():
                filters &= Q(bar_code__icontains=query)
            else:
                filters &= Q(name__icontains=query) | Q(category__name__icontains=query)

        return Product.objects.filter(filters)