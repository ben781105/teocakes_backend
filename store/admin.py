from django.contrib import admin
from .models import (
    Product, Category, Cart, CartItem,
    CustomCakeRequest, Order, OrderItem, ProductImage,Flavour, TikTokPost
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

@admin.register(TikTokPost)
class TikTokPostAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "active", "created_at")
    list_editable = ("order", "active")
    list_filter = ("active",)
    fields = ("cover", "caption", "url", "order", "active")
 