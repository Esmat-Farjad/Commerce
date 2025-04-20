from django.contrib import admin
from .models import Category, Products, Customer,SalesProducts,SalesDetails
# Register your models here.

admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Customer)
admin.site.register(SalesProducts)
admin.site.register(SalesDetails)
