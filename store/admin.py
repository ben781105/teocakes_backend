from django.contrib import admin
from .models import (
    Product, Category, Cart, CartItem,
    CustomCakeRequest, Order, OrderItem, ProductImage,Flavour
)


admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(CustomCakeRequest)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Flavour)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
