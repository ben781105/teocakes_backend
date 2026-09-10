from django.contrib import admin


from .models import Product, Category, Cart, CartItem,CustomCakeRequest,Order,OrderItem

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(CustomCakeRequest)
admin.site.register(Order)
admin.site.register(OrderItem)
