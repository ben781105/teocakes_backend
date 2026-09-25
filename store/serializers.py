from rest_framework import serializers
from .models import Product,Cart,CartItem,CustomCakeRequest,Order,OrderItem,Category,Flavour,ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    thumbnail = serializers.SerializerMethodField()
    class Meta:
        model = ProductImage
        fields = ["id", "image", "order","thumbnail"]

    def get_image(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if obj.image else None

    def get_thumbnail(self, obj):
        request = self.context.get("request")
        target = obj.thumbnail or obj.image
        return request.build_absolute_uri(target.url) if target else None


class FlavourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flavour
        fields = ["id", "name"]

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    gallery_images = ProductImageSerializer(many=True, read_only=True)
    flavours = FlavourSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

    def get_image(self, obj):
        request =self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_thumbnail(self, obj):
        request = self.context.get("request")
        target = obj.thumbnail or obj.image   # fall back if thumb missing
        return request.build_absolute_uri(target.url) if target else None

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    product_count = serializers.IntegerField(source='products.count', read_only=True)


    class Meta:
        model = Category
        fields = ["id", "name", "slug", "image", "description","product_count","thumbnail"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_thumbnail(self, obj):
        request = self.context.get("request")
        target = obj.thumbnail or obj.image
        return request.build_absolute_uri(target.url) if target else None

    def get_product_count(self, obj):
        return obj.products.filter(available=True).count()


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()
    flavour_name = serializers.CharField(source="flavour.name",read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "subtotal", "custom_message","flavour_name","flavour"]

    def get_subtotal(self, obj):
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["cart_id", "items", "total"]

class CustomCakeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomCakeRequest
        fields = [
            "id", "name", "phone_number", "description", "size",
            "flavor", "occasion", "date_needed", "budget",
            "reference_image", "additional_message", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_image = serializers.ImageField(source="product.image", read_only=True)
    flavour_name = serializers.CharField(source="flavour.name", read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "quantity",
            "price",
            "subtotal",
            "flavour_name",
            "custom_message"
        ]

    def get_subtotal(self, obj):
        return obj.price * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "phone_number",
            "total",
            "status",
            "created_at",
            "items",
        ]


   