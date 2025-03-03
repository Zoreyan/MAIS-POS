import django_filters
from django.forms import TextInput, Select
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    def __init__(self, *args, shop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['category'].queryset = Category.objects.filter(shop=shop)
    
    category = django_filters.ModelChoiceFilter(
        field_name="category",
        label="Категория",
        widget=Select(attrs={'class': 'form-select text-capitalize', 'id': 'ProductCategory'})
    )
    quantity_max = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="lte",
        label="Кол-во до",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Кол-во до:'})
    )
    quantity_min = django_filters.NumberFilter(
        field_name="quantity", lookup_expr="gte",
        label="Кол-во от",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Кол-во от:'})
    )
    price_max = django_filters.NumberFilter(
        field_name="sale_price", lookup_expr="lte",
        label="Цена до",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Цена до:'})
    )
    price_min = django_filters.NumberFilter(
        field_name="sale_price", lookup_expr="gte",
        label="Цена от",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Цена от:'})
    )
    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains",
        label="Название",
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Название:'})
    )