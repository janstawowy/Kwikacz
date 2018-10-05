from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.views import View
from kwik.models import Kwik, Messages, Comments, MyProfile
from kwik.forms import KwikForm, CreateUserForm, LoginForm, SendMessageForm, AddCommentForm, ChangePasswordForm, MyInfoForm, MyUiColourForm
from django.http import HttpResponse,  HttpResponseRedirect
from django.contrib.auth.models import User

# Create your views here.

#parent class handling ui colour and unread messages so i dont repeat myself
class BaseView(View):
    def getinfo(self, request):
        try:
            unread = Messages.objects.filter(towho=request.user).filter(seen=False).count()
        except TypeError:
            unread=0

        try:
            profile=MyProfile.objects.get(user=request.user)
            uicolour = profile.myuicolour
        except TypeError:
            uicolour="59, 126, 219"


        answer={"uicolour":uicolour,
               "unread":unread}
        return answer



#main page with all public content(kwiks) and a form to write one
class MainPageView(BaseView):

    def get(self, request):

        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        kwiki=Kwik.objects.all().order_by("-create_time")
        form = KwikForm()
        #get ui colour and number of unread messages
        answer=BaseView.getinfo(self,request)
        answer.update({"kwiks":kwiki,
                       "form":form})
        return render(request, 'kwiki.html', answer)

#form handling, adding new kwik to database, redirect back to main page
    def post(self, request):
        form=KwikForm(request.POST)

        if form.is_valid():
            content=form.cleaned_data['content']
            kwik=Kwik()
            kwik.content=content
            kwik.user=request.user
            kwik.save()
            return HttpResponseRedirect("")
        return HttpResponseRedirect("")


#kwik comments, form to add one
class ViewKwikView(BaseView):
    #kwik id is sent in url
    def get(self, request, kwik_id):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        kwik=get_object_or_404(Kwik, id=kwik_id)
        comments=Comments.objects.filter(whichkwik=kwik).order_by("create_time")
        form=AddCommentForm()
#get ui colour and unread messages
        answer=BaseView.getinfo(self,request)
        answer.update({"kwik":kwik,
                       "form":form,
                       "comments":comments})

        return render(request, 'kwik.html', answer)
#form handling, adding comment to database, redirect back to comments
    def post(self, request, kwik_id):

        form=AddCommentForm(request.POST)
        kwik = get_object_or_404(Kwik, id=kwik_id)
        if form.is_valid():
            content=form.cleaned_data['content']
            comment=Comments()
            comment.content=content
            comment.user=request.user
            comment.whichkwik=kwik
            comment.save()
            return HttpResponseRedirect(''.format(kwik_id))
        return HttpResponseRedirect(''.format(kwik_id))




#register new user
class AddUserView(BaseView):


    def get(self, request):
        form = CreateUserForm()
        #handling ui colour
        answer = BaseView.getinfo(self, request)
        answer.update({"form":form})
        return render (request, "adduser.html", answer)

#form handling, username and email must be unique, password and repeated password must match, if something goes wrong inform user, if everything i fine add user to database, log him and redirect to mainpage
    def post(self, request):
        form = CreateUserForm(request.POST)
        answer = BaseView.getinfo(self, request)
        answer.update({"form":form})
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
                        #password is hashed
                        User.objects.create_user(
                            username=username,
                            email=email,
                            password=password
                        )
                        user = authenticate(username=username, password=password)
                        if user is not None:
                            login(request, user)
                        return HttpResponseRedirect("/")
                    return render(request, "adduser.html",answer)
                return render(request,"adduser.html",answer)
        return render(request, "adduser.html", answer)

#log in to kwikacz
class LoginView(BaseView):


    def get(self, request):
        form = LoginForm()
        #get ui colour
        answer = BaseView.getinfo(self, request)
        answer.update({"form":form})
        return render(request, "loginuser.html", answer)

#form handling
    def post(self, request):
        #get ui colour
        answer = BaseView.getinfo(self, request)
        form = LoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            #get user from db by email entered by user, if no object match inform user that email or password is wrong
            try:
                userobject = User.objects.get(email=email)
                user = authenticate(username=userobject.username, password=password)
            except User.DoesNotExist:
                form.add_error('email', "Bledne haslo i/lub email")
                answer.update({"form": form})
                return render(request, "loginuser.html", answer)
            #if everything is fine log in user and redirect to main page
            if user is not None:
                login(request, user)
                return HttpResponseRedirect("/")
            #if password was wrong inform user that email or password he entered was not valid
            else:
                form.add_error('email', "Bledne haslo i/lub email")
                answer.update({"form": form})
                return render(request, "loginuser.html", answer)

#log out and redirect to login
class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("login")

#user info: about me, write private message all kwiks by that user
class UserView(BaseView):
    #reference to user is sent in url
    def get (self, request, username):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        user=get_object_or_404(User, username=username)
        kwiki=Kwik.objects.filter(user=user)
        #if somehow user has no profile info(additional model) due to some database data loss try except will handle this by setting about me to "no description"
        try:
            profile=MyProfile.objects.get(user=user)
            userinfo = profile.aboutme
        except TypeError:
            userinfo="Brak opisu"
        except MyProfile.DoesNotExist:
            userinfo="Brak opisu"

        answer=BaseView.getinfo(self,request)
        answer.update({"kwiks":kwiki,
                       "username":username,
                       "userinfo":userinfo})

        return render(request, "userdetails.html", answer)

#user panel, allows to change ui colour, add short description or change password warning: multiple forms on same page ahead
class MyInfoView(BaseView):
    def get(self, request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        user = User.objects.get(username=request.user)
        #if profile info was deleted from database  try except will add new entry witch default values
        try:
            profile = MyProfile.objects.get(user=user)
        except MyProfile.DoesNotExist:
            prof = MyProfile()
            prof.user = user
            prof.save()


        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')

        passwordform=ChangePasswordForm()
        myuicolourform=MyUiColourForm()
        myinfoform=MyInfoForm()

        answer=BaseView.getinfo(self,request)
        answer.update({"passwordform":passwordform,
                       "myuicolourform":myuicolourform,
                       "myinfoform":myinfoform})

        return render(request, 'editinfo.html',answer)
    def post(self, request):
        user = User.objects.get(username=request.user)
        profile=MyProfile.objects.get(user=user)
        #there are 3 forms on same page this part handles about me form
        if request.method == 'POST' and 'postinfoform' in request.POST:
            myinfoform=MyInfoForm (request.POST)
            if myinfoform.is_valid():
                myinfo=myinfoform.cleaned_data['myinfo']
                profile.aboutme=myinfo
                profile.save()
                return HttpResponseRedirect("")
        # there are 3 forms on same page this part handles ui colour form
        if request.method == 'POST' and 'postuicolourform' in request.POST:
            mycolourform=MyUiColourForm (request.POST)
            if mycolourform.is_valid():
                uicolour=mycolourform.cleaned_data['colour']
                profile.myuicolour=uicolour
                profile.save()
                return HttpResponseRedirect("")

        # there are 3 forms on same page this part handles change password form
        if request.method == 'POST' and 'postpasswordform' in request.POST:
            passwordform=ChangePasswordForm(request.POST)
            if passwordform.is_valid():

                currentpassword=passwordform.cleaned_data['currentpassword']
                password = passwordform.cleaned_data['password']
                password2 = passwordform.cleaned_data['password2']
                if currentpassword!=user.password:
                    passwordform.add_error('currentpassword', "bledne haslo")
                else:
                    if password!=password2:
                        passwordform.add_error("password", "podane hasla sie nie zgadzaja")
                    else:
                        user.password=password
                        user.save()
                        return HttpResponse('haslo zmienione')
                return render(request, 'editinfo.html', {"form": form})
            return render(request, 'editinfo.html', {"form": form})


#displays all conversations by date of last message, only last message is shown
class MessageView(BaseView):
    def get(self,request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        currentuser=User.objects.get(username=request.user)
#get messages sent by or to user. only last one for each conversation
        alist=Messages.objects.filter(Q(towho=currentuser)|Q(fromwho=currentuser)).distinct('towho', 'fromwho').order_by('towho', 'fromwho', "-date_sent")
        messages=list(alist)
        #remove doubles so if user sent and received message from another user only one will be shown.
        i=0
        while i <len(messages):
            j=1
            while j <len(messages):
                if messages[i].towho==messages[j].fromwho:
                    del messages[i]
                j+=1
            i+=1
#sort messages again by date after removing doubles
        for a in range(len(messages) - 1, 0, -1):
            for b in range(a):
                if messages[b].date_sent > messages[b + 1].date_sent:
                 temp = messages[b]
                 messages[b] = messages[b + 1]
                 messages[b + 1] = temp
#i useed some gerecric bubble sort code from stack overflow, so instead of rewriting it to sort in descending order i just reversed my list python way
        messages.reverse()

        answer=BaseView.getinfo(self,request)
        answer.update({"messages":messages,
                       "currentuser":currentuser})

        return render(request, 'messages.html', answer)


#conversation with another user
class ConversationView(BaseView):

    def get(self,request,username):
        form=SendMessageForm
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect('login')
        recipent=User.objects.get(username=username)
        currentuser = User.objects.get(username=request.user)
        #getting all messages to or from user you have conversation with
        messages=Messages.objects.filter((Q(towho=currentuser)&Q(fromwho=recipent))|(Q(fromwho=currentuser)&Q(towho=recipent))).order_by("-date_sent")
        #marking unseen messages as seen
        newmessages=Messages.objects.filter(Q(towho=currentuser)&Q(fromwho=recipent)).filter(seen=False)
        for message in newmessages:
            message.seen=True
            message.save()

        answer=BaseView.getinfo(self,request)
        answer.update({"form":form,
                       "messages":messages,
                       "currentuser":currentuser})

        return render(request, 'conversations.html', answer)

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











