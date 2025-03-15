from import_export import resources
from import_export.fields import Field
from .models import Product

class ProductResource(resources.ModelResource):
    category__name = Field(column_name='category')  # Указываем имя колонки как 'category'

    class Meta:
        model = Product
        fields = (
            'name', 'category__name', 'cost_price', 'sale_price', 'discount',
            'unit', 'bar_code', 'quantity', 'min_quantity'
        )
        export_order = fields

    def dehydrate_category__name(self, product):
        return product.category.name if product.category else ''