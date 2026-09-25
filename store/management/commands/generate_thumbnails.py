from django.core.management.base import BaseCommand
from django.db.models import Q
from store.models import Product, ProductImage,Category


class Command(BaseCommand):
    help = "Generate WebP thumbnails and resize oversized images"

    def handle(self, *args, **options):
        missing = Q(thumbnail="") | Q(thumbnail__isnull=True)

        for p in Product.objects.filter(missing):
            if not p.image:
                continue
            p._resize_main()
            p._make_thumbnail()
            p.save(update_fields=["image", "thumbnail"])
            self.stdout.write(self.style.SUCCESS(f"Product: {p.name}"))

        for gi in ProductImage.objects.filter(missing):
            if not gi.image:
                continue
            gi._resize_main()
            gi._make_thumbnail()
            gi.save(update_fields=["image", "thumbnail"])
            self.stdout.write(self.style.SUCCESS(f"Gallery: {gi}"))

        for c in Category.objects.filter(missing):
            if not c.image:
                continue
            c._resize_main()
            c._make_thumbnail()
            c.save(update_fields=["image", "thumbnail"])
            self.stdout.write(self.style.SUCCESS(f"Category: {c.name}"))