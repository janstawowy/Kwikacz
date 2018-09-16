from django import forms
from kwik.models import Kwik
from django.core.validators import EmailValidator, URLValidator, ValidationError

class KwikForm(forms.Form):
    content=forms.CharField(max_length=140,label="kwiknij!", help_text= "Nie kwicz dluzej niz 140 znakow!", widget=forms.Textarea)

class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=64, label="username")
    email=forms.CharField(max_length=64, label="email", validators=[EmailValidator()])
    password=forms.CharField(max_length=64, label="haslo", widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=64, label="powtorz haslo", widget=forms.PasswordInput)

class LoginForm(forms.Form):
    email=forms.CharField(max_length=64, label="email", validators=[EmailValidator()])
    password=forms.CharField(max_length=64, label="haslo", widget=forms.PasswordInput)