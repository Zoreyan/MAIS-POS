from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from apps.product.models import Product, Shop
from django.db.models import Q, Sum, F
from .serializers import ProductSerializer
from apps.user.models import User
from apps.utils.utils import generate_text
from .models import Payment
from .serializers import *
import logging
from django.db import transaction
from django.core.cache import cache
from rest_framework.decorators import action
from apps.history.models import *
from django.utils.timezone import now

logger = logging.getLogger(__name__)

class GetProduct(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        try:
            bar_code = request.GET.get('bar_code')
            product_id = request.GET.get('product_id')
            product = Product.objects.get(Q(id=product_id) | Q(bar_code=bar_code), shop=request.user.shop)  # Находим продукт по штрихкоду
            
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
            return Response(product_data, status=200)

        except Product.DoesNotExist:
            return Response({'status': 'error', 'message': 'Продукт не найден'}, status=404)


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
        cache_key = f'products_{query}_{self.request.user.shop.id}'  # Делаем уникальный ключ для кеша
        products = cache.get(cache_key)

        if not products:
            products = list(Product.objects.filter(filters))  # Превращаем QuerySet в список
            cache.set(cache_key, products, 3600)

        return products

class CheckUserExists(APIView):
    def get(self, request, *args, **kwargs):
        tg_id = request.GET.get('tg_id')

        # Проверка наличия tg_id
        if not tg_id:
            logger.error("Не передан tg_id в запросе")
            return Response({"error": "Необходимо указать tg_id"}, status=400)

        try:
            # Получаем пользователя за один запрос
            user = User.objects.filter(tg_id=tg_id).first()

            # Формируем контекст
            context = {
                'exists': user is not None,
                'has_access': user.has_access if user else False
            }

            logger.info(f"Проверка пользователя: tg_id={tg_id}, exists={context['exists']}, has_access={context['has_access']}")
            return Response(context, status=200)

        except Exception as e:
            logger.error(f"Ошибка при проверке пользователя: {e}")
            return Response({"error": "Внутренняя ошибка сервера"}, status=500)



class AuthView(APIView):
    def post(self, request, *args, **kwargs):
        user_phone = request.data.get("phone")  # Телефон из бота
        tg_id = request.data.get("tg_id")

        if not user_phone or not tg_id:
            return Response({"error": "Необходимо указать телефон и tg_id"}, status=400)

        try:
            with transaction.atomic():  # Используем транзакцию для атомарности
                password = generate_text()
                user = User.objects.create_user(
                    username=f"{user_phone}",
                    phone=user_phone,
                    password=password,
                    role='owner',
                    tg_id=tg_id
                )
                shop = Shop.objects.create(name=f'shop_{user_phone}')
                user.shop = shop
                user.save()

                logger.info(f"Создан пользователь: {user.username}, магазин: {shop.name}")

                return Response({
                    'phone': user_phone,
                    'password': password,  # Пароль лучше не возвращать в ответе
                    'shop': shop.name
                }, status=201)

        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            return Response({"error": "Пользователь с таким телефоном или tg_id уже существует"}, status=400)
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя: {e}")
            return Response({"error": "Внутренняя ошибка сервера"}, status=500)
        


class PaymentCreateView(APIView):

    def post(self, request, *args, **kwargs):
        image = request.FILES.get('file')

        if not image:
            return Response({'status': 'error', 'message': 'Необходимо загрузить изображение'}, status=400)

        try:
            user = User.objects.get(tg_id=request.data.get('tg_id'))
            Payment.objects.create(user=user, image=image)
            logger.info(f"Создан платеж для пользователя: {user.username}")
            return Response({'status': 'success'}, status=201)

        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            return Response({'status': 'error', 'message': 'Внутренняя ошибка сервера'}, status=500)
        


class CheckPaymentStatusView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            tg_id = request.GET.get('tg_id')
            user = User.objects.get(tg_id=tg_id)
            if user.has_access:
                return Response({'status': 'success', 'message': 'Платеж прошел успешно'}, status=200)
            else:
                return Response({'status': 'error', 'message': 'Платеж не прошел'}, status=400)
        except User.DoesNotExist as e:
            logger.error(f"Пользователь не найден: {e}")
            return Response({'status': 'error', 'message': 'Пользователь не найден'}, status=404)
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса платежа: {e}")
            return Response({'status': 'error', 'message': 'Внутренняя ошибка сервера'}, status=500)
        



# Вьюсет для статистики продаж
class TodayRevenue(viewsets.ViewSet):
    
    @action(detail=False, methods=['get'])
    def today_revenue(self, request):
        today = now().date()
        total_revenue = OrderHistory.objects.filter(created__date=today).aggregate(
            total=Sum('cash_payment') + Sum('online_payment')
        )["total"] or 0
        return Response({"today_revenue": total_revenue})
    
    @action(detail=False, methods=['get'])
    def order_history(self, request):
        orders = OrderHistory.objects.all()
        serializer = OrderHistorySerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sold_history(self, request):
        sales = SoldHistory.objects.all()
        serializer = SoldHistorySerializer(sales, many=True)
        return Response(serializer.data)