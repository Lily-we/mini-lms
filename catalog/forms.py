import json
from django import forms
from .models import ContentItem


class ContentItemAdminForm(forms.ModelForm):
    class Meta:
        model = ContentItem
        fields = "__all__"

    def clean_data(self):
        data = self.cleaned_data.get("data") or {}
        item_type = self.cleaned_data.get("type")

        if not isinstance(data, dict):
            raise forms.ValidationError("Data must be a JSON object (dictionary). Example: {\"text\": \"...\"}")

        # Validate keys per type
        if item_type == ContentItem.ItemType.TEXT:
            # allow: text
            if "text" not in data:
                raise forms.ValidationError("TEXT requires data.text. Example: {\"text\": \"Hello\"}")

        if item_type == ContentItem.ItemType.LINK:
            if "url" not in data:
                raise forms.ValidationError("LINK requires data.url. Example: {\"url\": \"https://...\"}")

        if item_type == ContentItem.ItemType.YOUTUBE:
            if ("youtube_id" not in data) and ("youtube_url" not in data):
                raise forms.ValidationError(
                    "YOUTUBE requires data.youtube_url or data.youtube_id. Example: "
                    "{\"youtube_url\": \"https://youtu.be/...\"}"
                )

        if item_type == ContentItem.ItemType.TELEGRAM:
            if "invite_url" not in data:
                raise forms.ValidationError("TELEGRAM requires data.invite_url. Example: {\"invite_url\": \"https://t.me/+...\"}")

        return data

    def clean(self):
        cleaned = super().clean()
        item_type = cleaned.get("type")

        # Optional: prevent attaching files to types that don't need it
        if item_type in {ContentItem.ItemType.YOUTUBE, ContentItem.ItemType.TEXT, ContentItem.ItemType.LINK, ContentItem.ItemType.TELEGRAM}:
            cleaned["asset"] = None

        return cleaned