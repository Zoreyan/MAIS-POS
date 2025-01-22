import django_filters
from django.forms import TextInput, Select

from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(
        field_name="sale_price", lookup_expr="gte",
        label="Цена от",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Цена от:'})
    )
    price_max = django_filters.NumberFilter(
        field_name="sale_price", lookup_expr="lte",
        label="Цена до",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Цена до:'})
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label="Категория",
        widget=Select(attrs={'class': 'form-select text-capitalize', 'id': 'ProductCategory'})
    )
    quantity_min = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="gte",
        label="Кол-во от",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Кол-во от:'})
    )
    quantity_max = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="lte",
        label="Кол-во до",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Кол-во до:'})
    )

    class Meta:
        model = Product
        fields = ['price_min', 'price_max', 'category', 'quantity_min', 'quantity_max']