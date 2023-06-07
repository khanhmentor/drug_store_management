from .models import User, CategoryType, CategoryItem, Order, Status, OrderItem
from django.contrib import admin

# Register your models here.

admin.site.register(User)
admin.site.register(CategoryType)
admin.site.register(CategoryItem)
admin.site.register(Status)
admin.site.register(Order)
admin.site.register(OrderItem)