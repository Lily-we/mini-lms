from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Section, ContentItem


@login_required
def home(request):
    sections = Section.objects.filter(is_published=True).order_by("order", "title")
    return render(request, "catalog/home.html", {"sections": sections})


@login_required
def section_detail(request, slug: str):
    section = get_object_or_404(Section, slug=slug, is_published=True)
    items = (
        ContentItem.objects
        .filter(section=section, is_published=True)
        .select_related("asset")
        .order_by("order", "title")
    )
    return render(request, "catalog/section_detail.html", {"section": section, "items": items})