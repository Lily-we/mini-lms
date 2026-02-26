from django.db import models
from django.utils.text import slugify
from .utils import extract_youtube_id

class Section(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "section"
            slug = base
            i = 2
            while Section.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class FileAsset(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="assets/")
    mime_type = models.CharField(max_length=120, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ContentItem(models.Model):
    class ItemType(models.TextChoices):
        TEXT = "TEXT", "Text"
        LINK = "LINK", "Link"
        YOUTUBE = "YOUTUBE", "YouTube"
        DRAWING = "DRAWING", "Drawing (PDF/PNG)"
        DXF = "DXF", "DXF (download)"
        ANIMATION = "ANIMATION", "Animation"
        QUIZ = "QUIZ", "Quiz"
        TELEGRAM = "TELEGRAM", "Telegram"

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ItemType.choices)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    # flexible payload (MVP)
    data = models.JSONField(default=dict, blank=True)

    # optional file link
    asset = models.ForeignKey(FileAsset, null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
    
    def save(self, *args, **kwargs):
    # Auto-derive youtube_id if admin pastes youtube_url
        if self.type == self.ItemType.YOUTUBE and isinstance(self.data, dict):
            youtube_id = self.data.get("youtube_id")
            youtube_url = self.data.get("youtube_url")
            if (not youtube_id) and youtube_url:
                vid = extract_youtube_id(youtube_url)
                if vid:
                # Make sure we assign back (JSONField change detection)
                    new_data = dict(self.data)
                    new_data["youtube_id"] = vid
                    self.data = new_data
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.section.title} · {self.title}"