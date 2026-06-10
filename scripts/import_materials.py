from pathlib import Path

from catalog.models import Section, FileAsset, ContentItem

BOOKS_DIR = Path("media/ebooks")
ARTICLES_DIR = Path("media/articles")


def import_folder(folder, section_name):
    section, _ = Section.objects.get_or_create(
        title=section_name,
        defaults={
            "description": section_name,
            "is_published": True,
        },
    )

    order = ContentItem.objects.filter(section=section).count()

    for file_path in sorted(folder.glob("*.pdf")):

        existing = ContentItem.objects.filter(
            section=section,
            title=file_path.stem
        ).exists()

        if existing:
            print(f"Skipping: {file_path.name}")
            continue

        asset = FileAsset.objects.create(
            title=file_path.stem,
            file=str(file_path.relative_to("media"))
        )

        ContentItem.objects.create(
            section=section,
            title=file_path.stem,
            type="DRAWING/BOOKS",
            asset=asset,
            order=order,
            is_published=True,
        )

        order += 1

        print(f"Imported: {file_path.name}")


def run():
    import_folder(BOOKS_DIR, "Elektron Kitoblar")
    import_folder(ARTICLES_DIR, "Maqolalar")

    print("Done.")