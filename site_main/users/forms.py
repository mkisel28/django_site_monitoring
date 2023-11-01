

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from main.models import TrackedWord


User = get_user_model()

class RegistrationForm(UserCreationForm):


    class Meta:
        model = User
        fields = ("username", "password1", "password2")

class TrackedWordForm(forms.ModelForm):
    class Meta:
        model = TrackedWord
        fields = ['keyword']