from django.urls import path
from . import views


urlpatterns = [
    path(
        "products/",
        views.products
    ),
    path(
        "favourites/",
        views.favourites
    ),
    path(
        "cart/<str:cart_id>/",
        views.get_cart,
        name="get-cart"
    ),
    path(
        "cart/<str:cart_id>/add/",
        views.add_to_cart,
        name="add-to-cart"
    ),
    path(
        "cart/<str:cart_id>/items/<int:item_id>/",
        views.cart_item_detail,
        name="cart-item-detail"
    ),
    path("cart/<str:cart_id>/set-phone/", 
         views.set_cart_phone, 
         name="set-cart-phone"),
    path("cart/by-phone/", 
         views.get_cart_by_phone, 
         name="get-cart-by-phone"),
]