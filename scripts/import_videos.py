import json
import os

from django.core.management.base import BaseCommand

from catalog.models import ContentItem, FileAsset, Section
from catalog.utils import extract_youtube_id


class Command(BaseCommand):
    help = "Import video content items from JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="Path to the JSON file containing video data"
        )
        parser.add_argument(
            "--media-dir", type=str, default="media",
            help="Base media directory (default: media)"
        )
        parser.add_argument(
            "--videos-subdir", type=str, default="videos",
            help="Subdirectory inside media-dir where local video files are stored (default: videos)"
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]
        media_dir = options["media_dir"]
        videos_subdir = options["videos_subdir"]

        # Load JSON
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to read JSON file: {e}"))
            return

        # Section
        section_title = data.get("section", "Video darsliklar")
        section, created = Section.objects.get_or_create(title=section_title)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created section: '{section_title}'"))
        else:
            self.stdout.write(f"Using existing section: '{section_title}'")

        items = data.get("items", [])
        success_count = 0
        error_count = 0

        for item in items:
            order = item.get("order", 0)
            title = item.get("title", f"Video {order}")
            item_type = item.get("type", "YOUTUBE")

            try:
                if item_type == "YOUTUBE":
                    url = item.get("url", "")
                    youtube_id = extract_youtube_id(url)

                    if not youtube_id:
                        # Could be a playlist — store as LINK instead
                        self.stdout.write(self.style.WARNING(
                            f"[{order}] Could not extract YouTube ID from: {url} — saving as LINK"
                        ))
                        ContentItem.objects.create(
                            section=section,
                            title=title,
                            type=ContentItem.ItemType.LINK,
                            order=order,
                            data={"url": url},
                        )
                    else:
                        ContentItem.objects.create(
                            section=section,
                            title=title,
                            type=ContentItem.ItemType.YOUTUBE,
                            order=order,
                            data={"youtube_id": youtube_id, "youtube_url": url},
                        )
                    self.stdout.write(f"[{order}] ✓ YOUTUBE — {title}")

                elif item_type == "ANIMATION":
                    filename = item.get("file", "")
                    file_path = os.path.join(media_dir, videos_subdir, filename)

                    if not os.path.exists(file_path):
                        self.stdout.write(self.style.WARNING(
                            f"[{order}] File not found: {file_path} — skipping"
                        ))
                        error_count += 1
                        continue

                    # Create FileAsset pointing to existing file
                    relative_path = f"{videos_subdir}/{filename}"
                    asset, _ = FileAsset.objects.get_or_create(
                        file=relative_path,
                        defaults={"title": title, "mime_type": "video/mp4"},
                    )

                    ContentItem.objects.create(
                        section=section,
                        title=title,
                        type=ContentItem.ItemType.ANIMATION,
                        order=order,
                        asset=asset,
                        data={},
                    )
                    self.stdout.write(f"[{order}] ✓ ANIMATION — {title}")

                else:
                    self.stdout.write(self.style.WARNING(
                        f"[{order}] Unknown type '{item_type}' — skipping"
                    ))
                    error_count += 1
                    continue

                success_count += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"[{order}] Error: {e}"))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! {success_count} imported, {error_count} skipped/errors."
        ))