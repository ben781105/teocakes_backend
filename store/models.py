from django.db import models
import uuid
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="categories/thumbs/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_image = self.image.name if self.image else None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

        image_changed = self.image and self.image.name != self._original_image

        if self.image and (not self.thumbnail or image_changed):
            self._resize_main()
            self._make_thumbnail()
            super().save(update_fields=["image", "thumbnail"])
            self._original_image = self.image.name

    def _resize_main(self):
        img = Image.open(self.image)
        if img.width <= 1200:
            return
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.thumbnail((1200, 1200), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=82)
        self.image.save(f"{self.slug}.webp", ContentFile(buffer.getvalue()), save=False)

    def _make_thumbnail(self):
        img = Image.open(self.image)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.thumbnail((500, 500), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=80)
        self.thumbnail.save(f"{self.slug}-thumb.webp", ContentFile(buffer.getvalue()), save=False)

    def __str__(self):
        return self.name
class Flavour(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    flavours = models.ManyToManyField(Flavour, blank=True)

    serving_size = models.CharField(max_length=100, blank=True, help_text="e.g. 'Serves 8-10'")

    prep_time = models.CharField(max_length=100, blank=True, help_text="e.g. '24-48 hours notice'")

    image = models.ImageField(
        upload_to="products/"
    )
    thumbnail = models.ImageField(upload_to="products/thumbs/", blank=True, null=True)

    favourite = models.BooleanField(default=False)

    available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_image = self.image.name if self.image else None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

        image_changed = self.image and self.image.name != self._original_image

         
        if self.image and (not self.thumbnail or image_changed):
            self._make_thumbnail()
            super().save(update_fields=["thumbnail"])
            self._original_image = self.image.name

    def _resize_main(self):
        img = Image.open(self.image)
        if img.width <= 1600:
            return
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.thumbnail((1600, 1600), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=82)
        self.image.save(f"{self.slug}.webp", ContentFile(buffer.getvalue()), save=False)


    def _make_thumbnail(self):
        img = Image.open(self.image)
        if img.mode not in ("RGB","RGBA"):
          img = img.convert("RGB")
        img.thumbnail((600, 600), Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=80)

        name = f"{self.slug}-thumb.webp"
        self.thumbnail.save(name, ContentFile(buffer.getvalue()), save=False)



    def __str__(self):
        return self.name


class Cart(models.Model):
    cart_id = models.CharField(
        max_length=100,
        unique=True
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def total(self):
        return sum(item.product.price * item.quantity for item in self.items.all())



    def __str__(self):
        return self.cart_id

class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    custom_message = models.CharField(max_length=200, blank=True, help_text="Message to write on the cake")
    flavour = models.ForeignKey(
        Flavour,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.product.name


class CustomCakeRequest(models.Model):
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)

    description = models.TextField()
    size = models.CharField(max_length=100, blank=True, null=True)  # e.g. "serves 20"
    flavor = models.CharField(max_length=100, blank=True, null=True)
    occasion = models.CharField(max_length=100, blank=True, null=True)
    date_needed = models.DateField(blank=True, null=True)
    budget = models.CharField(max_length=100, blank=True, null=True)
    reference_image = models.ImageField(upload_to="custom_requests/", blank=True, null=True)
    additional_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.created_at.strftime('%Y-%m-%d')}"

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent to WhatsApp"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_id} - {self.phone_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    custom_message = models.TextField(blank=True,null=True)
    flavour = models.ForeignKey(
        Flavour,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery_images"
    )
    image = models.ImageField(upload_to="products/gallery/")
    thumbnail = models.ImageField(upload_to="products/gallery/thumbs/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_image = self.image.name if self.image else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image_changed = self.image and self.image.name != self._original_image

        if self.image and (not self.thumbnail or image_changed):
            self._resize_main()
            self._make_thumbnail()
            super().save(update_fields=["image", "thumbnail"])
            self._original_image = self.image.name

    def _base_name(self):
        return f"{self.product.slug}-gallery-{self.order}"

    def _resize_main(self):
        img = Image.open(self.image)
        if img.width <= 1600:
            return
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.thumbnail((1600, 1600), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=82)
        self.image.save(f"{self._base_name()}.webp", ContentFile(buffer.getvalue()), save=False)

    def _make_thumbnail(self):
        img = Image.open(self.image)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.thumbnail((300, 300), Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=80)
        self.thumbnail.save(f"{self._base_name()}-thumb.webp", ContentFile(buffer.getvalue()), save=False)


    def __str__(self):
        return f"{self.product.name} - image {self.order}"

