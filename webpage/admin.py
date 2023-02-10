from django.contrib import admin
from . models import Customer, ProductList, AddedToCart, Orders, Logo

# Register your models here.

admin.site.register(Customer)
admin.site.register(ProductList)
admin.site.register(AddedToCart)
admin.site.register(Orders)

admin.site.register(Logo)

