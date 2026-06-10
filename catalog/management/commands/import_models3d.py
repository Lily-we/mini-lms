import json
import os

from django.core.management.base import BaseCommand

from catalog.models import ContentItem, FileAsset, Section


class Command(BaseCommand):
    help = "Import 3D GLB model content items from JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="Path to the JSON file"
        )
        parser.add_argument(
            "--media-dir", type=str, default="media",
            help="Base media directory (default: media)"
        )
        parser.add_argument(
            "--models-subdir", type=str, default="models3d",
            help="Subdirectory inside media-dir where GLB files are stored (default: models3d)"
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]
        media_dir = options["media_dir"]
        models_subdir = options["models_subdir"]

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read JSON: {e}"))
            return

        section_title = data.get("section", "3D Modellar")
        section_desc = data.get("description", "")

        section, created = Section.objects.get_or_create(
            title=section_title,
            defaults={"description": section_desc},
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created section: '{section_title}'"))
        else:
            self.stdout.write(f"Using existing section: '{section_title}'")

        count = 0
        errors = 0

        for item in data.get("items", []):
            order = item.get("order", 0)
            title = item.get("title", f"Model {order}")
            filename = item.get("file", "")

            file_path = os.path.join(media_dir, models_subdir, filename)

            if not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(
                    f"[{order}] File not found: {file_path} — skipping"
                ))
                errors += 1
                continue

            relative_path = f"{models_subdir}/{filename}"

            asset, asset_created = FileAsset.objects.get_or_create(
                file=relative_path,
                defaults={"title": title, "mime_type": "model/gltf-binary"},
            )

            ContentItem.objects.create(
                section=section,
                title=title,
                type=ContentItem.ItemType.MODEL3D,
                order=order,
                asset=asset,
                data={},
            )

            self.stdout.write(f"[{order}] ✓ MODEL3D — {title} ({filename})")
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {count} models imported, {errors} skipped."
        ))