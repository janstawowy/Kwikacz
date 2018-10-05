from django import forms
from kwik.models import Kwik
from django.core.validators import EmailValidator, URLValidator, ValidationError

class KwikForm(forms.Form):
    content=forms.CharField(max_length=140,label="Kwiknij!", help_text= "Nie kwicz dłuzej niż 140 znaków!", widget=forms.Textarea)

class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=64, label="Nazwa użytkownika")
    email=forms.CharField(max_length=64, label="Email", validators=[EmailValidator()])
    password=forms.CharField(max_length=64, label="Hasło", widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=64, label="Powtórz hasło", widget=forms.PasswordInput)

class LoginForm(forms.Form):
    email=forms.CharField(max_length=64, label="Email", validators=[EmailValidator()])
    password=forms.CharField(max_length=64, label="Hasło", widget=forms.PasswordInput)

class SendMessageForm(forms.Form):
    content=forms.CharField(label="Wiadomosc prywatna", widget=forms.Textarea)

class AddCommentForm(forms.Form):
    content=forms.CharField(max_length=140, label="Napisz odpowiedź")

class ChangePasswordForm(forms.Form):
    currentpassword=forms.CharField(max_length=64, label="Aktualne hasło", widget=forms.PasswordInput)
    password = forms.CharField(max_length=64, label="Hasło", widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=64, label="Powtorz hasło", widget=forms.PasswordInput)

class MyInfoForm(forms.Form):
    myinfo=forms.CharField(max_length=140, label="O mnie")

class MyPhoneNumber(forms.Form):
    myphone=forms.IntegerField()

class MyUiColourForm(forms.Form):
    CHOICES = (('59, 126, 219', "niebieski" ),
               ("255, 225, 0", "żółty" ),
               ("100, 225, 50", "zielony" ),
               ("255, 50, 50 ", "czerwony" ),
               ("255, 192, 203 ", "różowy" ))

    colour = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect())