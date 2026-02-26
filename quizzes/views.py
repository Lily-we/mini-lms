from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Quiz, QuizAttempt, Answer, Choice


@login_required
def quiz_start(request, quiz_id: int):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    attempt = QuizAttempt.objects.create(quiz=quiz, user=request.user)
    return redirect("quiz_take", attempt_id=attempt.id)


@login_required
def quiz_take(request, attempt_id: int):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
    if attempt.is_submitted:
        return redirect("quiz_result", attempt_id=attempt.id)

    quiz = attempt.quiz
    questions = quiz.questions.prefetch_related("choices").all()

    if request.method == "POST":
        # Save answers
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

        # Compute score and submit
        answers = attempt.answers.select_related("selected_choice").all()
        total = questions.count()
        if total ==0:
            return render(request, "quizzes/quiz_take.html", {
                "attempt": attempt, "quiz": quiz, "questions": questions,
                "error": "No questions in this quiz yet. Ask admin to add questions."
            }) 
        score = 0
        for a in answers:
            if a.selected_choice and a.selected_choice.is_correct:
                score += 1

        attempt.total = total
        attempt.score = score
        attempt.submitted_at = timezone.now()
        attempt.save(update_fields=["total", "score", "submitted_at"])

        return redirect("quiz_result", attempt_id=attempt.id)

    return render(request, "quizzes/quiz_take.html", {"attempt": attempt, "quiz": quiz, "questions": questions})


@login_required
def quiz_result(request, attempt_id: int):
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, user=request.user)
    if not attempt.is_submitted:
        # results NOT allowed before submit (client requirement)
        return HttpResponseForbidden("Quiz results are available only after submission.")

    quiz = attempt.quiz
    questions = quiz.questions.prefetch_related("choices").all()
    answers = {a.question_id: a for a in attempt.answers.select_related("selected_choice")}

    return render(
        request,
        "quizzes/quiz_result.html",
        {"attempt": attempt, "quiz": quiz, "questions": questions, "answers": answers},
    )