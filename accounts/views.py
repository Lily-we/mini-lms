from django.contrib.auth import login
from django.shortcuts import redirect, render
from .forms import MinimalUserCreationForm


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