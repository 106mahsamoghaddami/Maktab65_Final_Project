from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from .forms import SignUpForm, SendNewEmailForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Amail


def home(request):
    return render(request, 'main/base.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            save_form = form.save(commit=False)
            save_form.set_password(form.cleaned_data.get('password'))
            save_form.save()
            messages.success(request, 'User registered successfully')
            return HttpResponseRedirect('/main/register')
        else:

            return render(request, 'main/signup.html', {'form': form})
    elif request.method == 'GET':
        form = SignUpForm()
    return render(request, 'main/signup.html', {'form': form})


def activate_mail(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=uid)
        if user is not None:
            user.is_verified = True
            user.save()
            messages.success(request, 'Email confirmation done successfully')
            return HttpResponseRedirect('/main/login')
    except User.DoesNotExist:
        messages.error(request, "Please sign up")
        return HttpResponseRedirect('/main/signup')


def Login(request):
    if request.method == 'GET':
        return render(request, 'main/login.html')
    elif request.method == 'POST':
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f' welcome {username} !!')
                return HttpResponseRedirect("/main/personal_page")
            else:
                messages.info(request, 'Incorrect credential')
                return render(request, "main/login.html")


def logout_view(request):
    if request.method == 'GET':
        return render(request, "main/logout.html")
    elif request.method == 'POST':
        logout(request)
        return HttpResponseRedirect("/main/")


class PersonalPage(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "main/personal_page.html")


class SendNewEmail(LoginRequiredMixin, View):
    def get(self, request):
        form = SendNewEmailForm()
        return render(request, "main/send_new_email_form.html", {'form': form})

    def post(self, request):
        form = SendNewEmailForm(request.POST, request.FILES)
        if form.is_valid():
            sender_email = User.objects.get(pk=request.user.id)
            new_email = Amail(sender_email=sender_email,
                              receiver_email=form.cleaned_data['receiver_email'],
                              cc=form.cleaned_data['cc'],
                              bcc=form.cleaned_data['bcc'],
                              subject=form.cleaned_data['subject'],
                              text=form.cleaned_data['text'],
                              file=form.cleaned_data['file'], )
            new_email.save()
            messages.success(request,f"email send successfully to {form.cleaned_data['receiver_email']}")

            return HttpResponseRedirect("/main/personal_page")


class Inbox(LoginRequiredMixin, View):
    def get(self, request):
        receiver = User.objects.get(pk=request.user.id)

        receiver_email = receiver.email
        inbox_emails = Amail.objects.filter(receiver_email=receiver_email)
        return render(request, "main/personal_page.html", {"inbox_emails": inbox_emails})


class Sent(LoginRequiredMixin, View):
    def get(self, request):
        sender = User.objects.get(pk=request.user.id)
        sent_emails = Amail.objects.filter(sender_email=sender)
        return render(request,"main/sent.html",{"sent_emails":sent_emails})


class AmailDetail(DetailView):
    model = Amail

