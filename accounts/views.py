from django.contrib.auth import login
from django.shortcuts import redirect, render
from .forms import MinimalUserCreationForm
from django.contrib.auth.decorators import login_required
from config.openai_config import openai


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = MinimalUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = MinimalUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})

@login_required
def ai_chat(request):
    answer = ""
    user_message = ""
    if request.method == "POST":
        user_message = request.POST.get("message")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )
        answer = response.choices[0].message.content

    return render(request, "accounts/chat.html", {
        "answer": answer,
        "user_message": user_message
    })