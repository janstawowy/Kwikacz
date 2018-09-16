from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views import View
from kwik.models import Kwik
from kwik.forms import KwikForm, CreateUserForm, LoginForm
from django.http import HttpResponse,  HttpResponseRedirect
from django.contrib.auth.models import User

# Create your views here.


class MainPageView(View):

    def get(self, request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        kwiki=Kwik.objects.all()
        answer={"kwiks":kwiki}
        return render(request, 'kwiki.html', answer)

class AddKwikView(View):
    def get(self, request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        form=KwikForm()
        return render(request, "kwiknij.html", {"form":form})
    def post(self, request):
        form=KwikForm(request.POST)

        if form.is_valid():
            content=form.cleaned_data['content']
            kwik=Kwik()
            kwik.content=content
            kwik.user=request.user
            kwik.save()
            return HttpResponseRedirect("")

class AddUserView(View):


    def get(self, request):
        form = CreateUserForm()
        return render (request, "adduser.html", {"form":form})

    def post(self, request):
        form = CreateUserForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            password2=form.cleaned_data['password2']
            email_count = User.objects.filter(email=email).count()
            if email_count > 0:
                form.add_error("email", "Ten email jest juz zajety")
            else:
                user_count = User.objects.filter(username=username).count()
                if user_count > 0:
                    form.add_error("username", "Ta nazwa uzytkownika jest juz zajeta")
                else:
                    if password != password2:
                        form.add_error('password', 'Hasla sie nie zgadzaja')
                    else:
                        hashedpassword=User.set_password(self, password)
                        User.objects.create_user(
                            username=username,
                            email=email,
                            password=hashedpassword
                        )
                        user = authenticate(username=username, password=password)
                        if user is not None:
                            login(request, user)
                        return HttpResponseRedirect("")
                    return render(request, "adduser.html", {"form": form})
                return render(request,"adduser.html", {"form": form})


class LoginView(View):


    def get(self, request):
        form = LoginForm()
        return render(request, "loginuser.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            userobject = User.objects.filter(email=email)
            username=userobject[0].username
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect("")
            else:
                form.add_error('email', "Bledne haslo i/lub email")

        return render(request, "loginuser.html", {"form": form})



class UserView(View):
    def get (self, request, username):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        user=get_object_or_404(User, username=username)
        kwiki=Kwik.objects.filter(username=user)
        answer={"username":username,
                "kwiks":kwiki}
        return render(request, "userdetails.html", answer)



