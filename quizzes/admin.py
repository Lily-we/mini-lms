from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    fields = ("text", "choice_image", "is_correct")

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "order", "difficulty", "text")
    list_filter = ("quiz", "difficulty")
    fields = ("quiz", "order", "difficulty", "text", "question_image")
    inlines = [ChoiceInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("quiz", "user", "difficulty", "started_at", "submitted_at", "score", "total")
    list_filter = ("quiz", "difficulty", "submitted_at")