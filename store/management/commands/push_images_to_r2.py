import os
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from pathlib import Path
from django.conf import settings
from store.models import Product, ProductImage, Category


class Command(BaseCommand):
    help = "Upload locally-stored media files to remote storage"

    def handle(self, *args, **options):
        local_root = Path(settings.BASE_DIR) / "media"

        for model, fields in [
            (Product, ["image", "thumbnail"]),
            (ProductImage, ["image", "thumbnail"]),
            (Category, ["image", "thumbnail"]),
        ]:
            for obj in model.objects.all():
                changed = []
                for field in fields:
                    f = getattr(obj, field)
                    if not f:
                        continue
                    source = local_root / f.name
                    if not source.exists():
                        self.stdout.write(f"missing locally: {f.name}")
                        continue
                    basename = os.path.basename(f.name)
                    with open(source, "rb") as fh:
                        f.save(basename, ContentFile(fh.read()), save=False)
                    changed.append(field)
                if changed:
                    obj.save(update_fields=changed)
                    self.stdout.write(self.style.SUCCESS(f"{model.__name__}: {obj}"))