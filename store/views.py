from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product,Cart,CartItem
from .serializers import ProductSerializer,CartSerializer


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

    if not product_id:
        return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    if quantity < 1:
        return Response({"error": "quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id, available=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    cart, _ = Cart.objects.get_or_create(cart_id=cart_id)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity}
    )

    if not created:
        item.quantity += quantity
        item.save()

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

    # if another cart already claimed this number, merge its items into the current cart
    existing = Cart.objects.filter(phone_number=phone).exclude(id=cart.id).first()
    if existing:
        for item in existing.items.all():
            current_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=item.product,
                defaults={"quantity": item.quantity}
            )
            if not created:
                current_item.quantity += item.quantity
                current_item.save()
        existing.delete()

    cart.phone_number = phone
    cart.save()

    serializer = CartSerializer(cart, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def get_cart_by_phone(request):
    phone = request.query_params.get("phone")

    if not phone:
        return Response({"error": "phone query param is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        cart = Cart.objects.get(phone_number=phone)
    except Cart.DoesNotExist:
        return Response({"error": "No cart found for this number"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CartSerializer(cart, context={"request": request})
    return Response(serializer.data)