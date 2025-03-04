from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.product.models import Product, Shop
from django.db.models import Q
from .serializers import ProductSerializer
from apps.user.models import User


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



class SignUpView(generics.CreateAPIView):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        shop_name = request.POST.get('shop')
        user = User.objects.filter(username=username).exists()
        if user:
            return Response({'status': 'error', 'message': 'Пользователь с таким именем уже существует'}, status=400)
        else:
            shop = Shop.objects.create(name=shop_name)
            User.objects.create_user(username=username, password=password, shop=shop, role='owner')
            return Response({'status': 'success', 'message': 'Пользователь успешно создан'}, status=201)


class CheckUserExists(APIView):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        user = User.objects.filter(username=username).exists()
        return Response({'exists': user}, status=200)