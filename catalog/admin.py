from django.contrib import admin
from .models import Section, ContentItem, FileAsset
from .forms import ContentItemAdminForm

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_published")
    list_editable = ("order", "is_published")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(FileAsset)
class FileAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "mime_type", "uploaded_at")



@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    form = ContentItemAdminForm
    list_display = ("title", "section", "type", "order", "is_published")
    list_filter = ("type", "is_published", "section")
    list_editable = ("order", "is_published")
    search_fields = ("title", "section__title")