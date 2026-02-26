from django.conf import settings
from django.db import models
from catalog.models import ContentItem


class Quiz(models.Model):
    # Link quiz to a ContentItem where type=QUIZ
    content_item = models.OneToOneField(
        ContentItem,
        on_delete=models.CASCADE,
        related_name="quiz",
        limit_choices_to={"type": ContentItem.ItemType.QUIZ},
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    pass_score = models.PositiveIntegerField(default=0)  # optional

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    @property
    def is_submitted(self) -> bool:
        return self.submitted_at is not None

    def __str__(self):
        return f"{self.user} - {self.quiz} ({'submitted' if self.is_submitted else 'in progress'})"


class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ("attempt", "question")