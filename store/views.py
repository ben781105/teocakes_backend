from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Category, Product,Cart,CartItem,OrderItem,Order,Flavour
from .serializers import CategorySerializer, ProductSerializer,CartSerializer,CustomCakeRequestSerializer,OrderSerializer
from django.db import transaction

@api_view(["GET"])
def products(request):

    products = Product.objects.filter(
        available=True
    )

    serializer = ProductSerializer(
        products,
        many=True,
        context={"request": request},
    )

    return Response(serializer.data)

@api_view(["GET"])
def favourites(request):
    products = Product.objects.filter(available=True, favourite=True)

    serializer = ProductSerializer(
        products,
        many=True,
        context={"request": request}
    )

    return Response(serializer.data)

@api_view(["GET"])
def get_cart(request, cart_id):
    cart, _ = Cart.objects.get_or_create(cart_id=cart_id)
    serializer = CartSerializer(cart, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
def add_to_cart(request, cart_id):
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))
    custom_message = request.data.get("custom_message", "").strip()
    flavour_id = request.data.get("flavour_id")

    if not product_id:
        return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    if quantity < 1:
        return Response({"error": "quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id, available=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    flavour = None
    if flavour_id:
        try:
            flavour = Flavour.objects.get(id=flavour_id)
        except Flavour.DoesNotExist:
            return Response({"error": "Flavour not found"}, status=status.HTTP_404_NOT_FOUND)

    cart, _ = Cart.objects.get_or_create(cart_id=cart_id)

    # Same cake with the same message and flavour merges; different config = new line
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        custom_message=custom_message,
        flavour=flavour,
        defaults={"quantity": quantity}
    )

    if not created:
        item.quantity += quantity
        item.save()

    print("RAW DATA:", request.data)
    print("PARSED MESSAGE:", repr(custom_message))

    serializer = CartSerializer(cart, context={"request": request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["PATCH", "DELETE"])
def cart_item_detail(request, cart_id, item_id):
    try:
        cart = Cart.objects.get(cart_id=cart_id)
        item = CartItem.objects.get(id=item_id, cart=cart)
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        quantity = int(request.data.get("quantity", item.quantity))
        if quantity < 1:
            return Response({"error": "quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)
        item.quantity = quantity
        item.save()

    elif request.method == "DELETE":
        item.delete()

    serializer = CartSerializer(cart, context={"request": request})
    return Response(serializer.data)

@api_view(["PATCH"])
def set_cart_phone(request, cart_id):
    phone = request.data.get("phone_number")

    if not phone:
        return Response({"error": "phone_number is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    if not cart.items.exists():
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        cart.phone_number = phone
        cart.save()

       
        order = Order.objects.create(phone_number=phone, total=cart.total)
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                custom_message=item.custom_message,
                flavour=item.flavour,
                 
            )

        
        cart.items.all().delete()
        cart.save()

    order_serializer = OrderSerializer(order, context={"request": request})
    cart_serializer = CartSerializer(cart, context={"request": request})

    return Response({
        "order": order_serializer.data,
        "cart": cart_serializer.data,
    })

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_custom_request(request):
    serializer = CustomCakeRequestSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



