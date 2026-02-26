from django.urls import path
from . import views

urlpatterns = [
    path("quiz/<int:quiz_id>/start/", views.quiz_start, name="quiz_start"),
    path("attempt/<int:attempt_id>/take/", views.quiz_take, name="quiz_take"),
    path("attempt/<int:attempt_id>/result/", views.quiz_result, name="quiz_result"),
]