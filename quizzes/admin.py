from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, Answer

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "order", "difficulty", "text")
    list_filter = ("quiz", "difficulty")
    inlines = [ChoiceInline]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "content_item")
    search_fields = ("title", "content_item__title")

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("quiz", "user", "difficulty", "started_at", "submitted_at", "score", "total")
    list_filter = ("quiz", "difficulty", "submitted_at")