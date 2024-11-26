# chatbot/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)