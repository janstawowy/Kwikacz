from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.views import View
from kwik.models import Kwik, Messages
from kwik.forms import KwikForm, CreateUserForm, LoginForm, SendMessageForm
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
                        User.objects.create_user(
                            username=username,
                            email=email,
                            password=password
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

class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponse("wylogowano")

class UserView(View):
    def get (self, request, username):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        user=get_object_or_404(User, username=username)
        kwiki=Kwik.objects.filter(user=user)
        answer={"username":username,
                "kwiks":kwiki}
        return render(request, "userdetails.html", answer)

class MessageView(View):
    def get(self,request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        currentuser=User.objects.get(username=request.user)
        alist=Messages.objects.filter(Q(towho=currentuser)|Q(fromwho=currentuser)).distinct('towho', 'fromwho').order_by('towho', 'fromwho', "-date_sent")
        messages=list(alist)
        i=0
        while i <len(messages):
            j=1
            while j <len(messages):
                if messages[i].towho==messages[j].fromwho:
                    del messages[i]
                j+=1
            i+=1

        for a in range(len(messages) - 1, 0, -1):
            for b in range(a):
                if messages[b].date_sent > messages[b + 1].date_sent:
                 temp = messages[b]
                 messages[b] = messages[b + 1]
                 messages[b + 1] = temp

        messages.reverse()

        return render(request, 'messages.html', {"messages":messages,
                                                 "currentuser":currentuser})

class SendMessageView(View):
    def get(self, request, username):
        form=SendMessageForm
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        return render(request, 'kwiknij.html', {'form':form})

    def post(self, request, username):
        form=SendMessageForm(request.POST)
        if form.is_valid():
            content=form.cleaned_data['content']
            towho=User.objects.get(username=username)
            msg=Messages()
            msg.content=content
            msg.towho=towho
            msg.fromwho=request.user
            msg.save()
            return HttpResponseRedirect("")

class ConversationView(View):
    def get(self,request,username):
        form=SendMessageForm
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        recipent=User.objects.get(username=username)
        currentuser = User.objects.get(username=request.user)
        messages=Messages.objects.filter((Q(towho=currentuser)&Q(fromwho=recipent))|(Q(fromwho=currentuser)&Q(towho=recipent))).order_by("-date_sent")

        return render(request, 'conversations.html', {"messages": messages})











