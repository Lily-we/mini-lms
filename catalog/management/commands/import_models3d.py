import json

from django.core.management.base import BaseCommand

from catalog.models import ContentItem, Section


class Command(BaseCommand):
    help = "Import 3D model content items from JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="Path to the JSON file"
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]

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
        for item in data.get("items", []):
            order = item.get("order", 0)
            title = item.get("title", f"Model {order}")
            model_key = item.get("model_key", "")

            ContentItem.objects.create(
                section=section,
                title=title,
                type=ContentItem.ItemType.MODEL3D,
                order=order,
                data={"model_key": model_key},
            )
            self.stdout.write(f"[{order}] ✓ MODEL3D — {title} (key: {model_key})")
            count += 1

        self.stdout.write(self.style.SUCCESS(f"\nDone! {count} models imported."))