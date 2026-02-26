from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("s/<slug:slug>/", views.section_detail, name="section_detail"),
]