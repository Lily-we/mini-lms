from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Section, ContentItem

# If you use Telegram gating
from quizzes.models import Quiz, QuizAttempt


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

    # --- Telegram gating context (safe even if no TELEGRAM items) ---
    required_ids = set()
    for it in items:
        if it.type == ContentItem.ItemType.TELEGRAM and isinstance(it.data, dict):
            rq = it.data.get("required_quiz_id")
            if isinstance(rq, str) and rq.isdigit():
                rq = int(rq)
            if isinstance(rq, int):
                required_ids.add(rq)

    available_quiz_ids = set(Quiz.objects.filter(id__in=required_ids).values_list("id", flat=True))

    completed_quiz_ids = set(
        QuizAttempt.objects.filter(
            user=request.user,
            submitted_at__isnull=False,
            quiz_id__in=available_quiz_ids,
        ).values_list("quiz_id", flat=True)
    )

    return render(
        request,
        "catalog/section_detail.html",
        {
            "section": section,
            "items": items,
            "available_quiz_ids": list(available_quiz_ids),
            "completed_quiz_ids": list(completed_quiz_ids),
        },
    )