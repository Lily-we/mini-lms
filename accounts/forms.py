from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class MinimalUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove Django's long help texts
        for name in ("username", "password1", "password2"):
            self.fields[name].help_text = ""

        # Simple labels (optional)
        self.fields["username"].label = "Username"
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm password"

        # Optional: add placeholders
        self.fields["username"].widget.attrs.update({"placeholder": "username"})
        self.fields["password1"].widget.attrs.update({"placeholder": "password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "repeat password"})