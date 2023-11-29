from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

class CustomLoginForm(AuthenticationForm):
    # You can add custom fields or methods if needed
    pass
