from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer


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