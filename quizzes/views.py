from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import OuterRef, Subquery, F
from .models import Quiz, QuizAttempt, Answer, Choice, Difficulty


@login_required
def my_attempts(request):
    attempts = (
        QuizAttempt.objects
        .filter(user=request.user)
        .select_related("quiz")
        .order_by("-started_at")
    )
    return render(request, "quizzes/my_attempts.html", {"attempts": attempts})


@login_required
def quiz_start(request, quiz_id: int):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    level = request.GET.get("level")
    if level not in Difficulty.values:
        return render(request, "quizzes/quiz_level.html", {"quiz": quiz})

    existing = QuizAttempt.objects.filter(
        quiz=quiz,
        user=request.user,
        submitted_at__isnull=True,
        difficulty=level,
    ).first()

    if existing:
        return redirect("quiz_take", attempt_id=existing.id)

    attempt = QuizAttempt.objects.create(quiz=quiz, user=request.user, difficulty=level)
    return redirect("quiz_take", attempt_id=attempt.id)


@login_required
def quiz_take(request, attempt_id: int):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
    if attempt.is_submitted:
        return redirect("quiz_result", attempt_id=attempt.id)

    quiz = attempt.quiz
    questions = quiz.questions.prefetch_related("choices").filter(difficulty=attempt.difficulty)

    if request.method == "POST":
        # Save answers (create/update Answer row for every question)
        for q in questions:
            choice_id = request.POST.get(f"q_{q.id}")
            selected = None
            if choice_id:
                selected = Choice.objects.filter(id=choice_id, question=q).first()

            Answer.objects.update_or_create(
                attempt=attempt,
                question=q,
                defaults={"selected_choice": selected},
            )

        total = questions.count()
        if total == 0:
            return render(request, "quizzes/quiz_take.html", {
                "attempt": attempt,
                "quiz": quiz,
                "questions": questions,
                "error": "No questions in this quiz yet. Ask admin to add questions."
            })

        # ✅ Only answers for these questions (difficulty-specific)
        answers = attempt.answers.select_related("selected_choice").filter(question__in=questions)

        score = 0
        for a in answers:
            if a.selected_choice and a.selected_choice.is_correct:
                score += 1

        attempt.total = total
        attempt.score = score
        attempt.submitted_at = timezone.now()
        attempt.save(update_fields=["total", "score", "submitted_at"])

        return redirect("quiz_result", attempt_id=attempt.id)

    return render(request, "quizzes/quiz_take.html", {
        "attempt": attempt,
        "quiz": quiz,
        "questions": questions
    })


@login_required
def quiz_result(request, attempt_id: int):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
    if not attempt.is_submitted:
        return HttpResponseForbidden("Quiz results are available only after submission.")

    quiz = attempt.quiz
    questions = quiz.questions.prefetch_related("choices").filter(difficulty=attempt.difficulty)

    answers_qs = attempt.answers.select_related("selected_choice").filter(question__in=questions)

    correct = answers_qs.filter(selected_choice__is_correct=True).count()
    wrong = answers_qs.filter(selected_choice__isnull=False, selected_choice__is_correct=False).count()
    skipped = answers_qs.filter(selected_choice__isnull=True).count()

    duration_seconds = 0
    if attempt.submitted_at and attempt.started_at:
        duration_seconds = int((attempt.submitted_at - attempt.started_at).total_seconds())
    mins, secs = divmod(duration_seconds, 60)
    duration_str = f"{mins}m {secs}s"

    answers = {a.question_id: a for a in answers_qs}

    # ---- Leaderboard (Telegram-quiz style)
    # Rule: leaderboard is based on the FIRST submitted attempt per user,
    # so retake does NOT change their leaderboard position.
    submitted = QuizAttempt.objects.filter(
        quiz=quiz,
        difficulty=attempt.difficulty,
        submitted_at__isnull=False,
    )

    first_id_subq = (
        submitted.filter(user=OuterRef("user"))
        .order_by("submitted_at")
        .values("id")[:1]
    )

    first_attempts = (
        submitted.annotate(first_id=Subquery(first_id_subq))
        .filter(id=F("first_id"))
        .select_related("user")
    )

    entries = list(first_attempts)

    # compute duration for sorting and display
    for e in entries:
        if e.submitted_at and e.started_at:
            e.dur_seconds = int((e.submitted_at - e.started_at).total_seconds())
        else:
            e.dur_seconds = 10**9
        m, s = divmod(e.dur_seconds, 60)
        e.dur_str = f"{m}m {s}s"


    # Sort: score desc, duration asc, submitted_at asc
    entries.sort(key=lambda e: (-e.score, e.dur_seconds, e.submitted_at))

    total_participants = len(entries)
    rank = None
    percentile = None

    user_entry = next((e for e in entries if e.user_id == request.user.id), None)
    if user_entry and total_participants:
        rank = entries.index(user_entry) + 1
        # Telegram-like: (people at or below you) / total
        percentile = round(100 * (total_participants - rank + 1) / total_participants)

    leaderboard_top = entries[:10]

    return render(
        request,
        "quizzes/quiz_result.html",
        {
            "attempt": attempt,
            "quiz": quiz,
            "questions": questions,
            "answers": answers,
            "correct": correct,
            "wrong": wrong,
            "skipped": skipped,
            "duration_str": duration_str,
            "rank": rank,
            "total_participants": total_participants,
            "percentile": percentile,
            "leaderboard_top": leaderboard_top,
        },
    )