from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from .forms import SignUpForm, SendNewEmailForm , NewContactForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Amail , Contacts


def home(request):
    return render(request, 'main/base.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            save_form = form.save(commit=False)
            save_form.set_password(form.cleaned_data.get('password'))
            save_form.save()
            messages.success(request, 'Your information has been successfully registered')
            messages.warning(request,
                             ' WARNING : Your registration will not be finalized without confirmation email so '
                             'you will not be able to log in')
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
            if user and user.is_verified == True:
                login(request, user)
                # messages.success(request, f' welcome {user.username} !!')
                return HttpResponseRedirect("/main/personal_page")
            else:
                messages.error(request, 'Incorrect credential')
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
            sender = User.objects.get(pk=request.user.id)  # that user is login in system

            receiver = form.cleaned_data['receiver_email']
            cc_email = form.cleaned_data['cc']
            bcc_email = form.cleaned_data['bcc']

            # for save in interface table we need to receivers id  and only this solution answered
            receiver_id = list(receiver.filter().values_list('id')[0])[0]
            cc_id = list(cc_email.filter().values_list('id')[0])[0]
            bcc_id = list(bcc_email.filter().values_list('id')[0])[0]

            # for make new instance of Amail class first create that fields are not many to many to other class
            new_email = Amail.objects.create(sender_email=sender,
                                             subject=form.cleaned_data['subject'],
                                             text=form.cleaned_data['text'],
                                             file=form.cleaned_data['file'],
                                             is_sent = True
                                             )

            new_email.receiver_email.add(receiver_id)
            new_email.cc.add(cc_id)
            new_email.bcc.add(bcc_id)
            new_email.save()

            messages.success(request, f"email send successfully to {receiver} and others")

            return HttpResponseRedirect("/main/personal_page")


class Inbox(LoginRequiredMixin, View):
    # from emails give me that emails receivers and cc and bcc is my user name(login user)
    def get(self, request):
        receiver = User.objects.get(pk=request.user.id)

        receiver_id= receiver.id
        inbox_emails1 = Amail.objects.filter(receiver_email__receive_emails__receiver_email=receiver_id)
        inbox_emails2 = Amail.objects.filter(cc__receive1_emails__cc=receiver_id)
        inbox_emails3 = Amail.objects.filter(bcc__receive2_emails__bcc=receiver_id)

        # print(inbox_emails2)

        return render(request, "main/personal_page.html", {"inbox_emails1": inbox_emails1,
                                                           "inbox_emails2":inbox_emails2,
                                                           "inbox_emails3":inbox_emails3})


class Sent(LoginRequiredMixin, View):
    # from emails give me that emails sender is my user name(login user)
    def get(self, request):
        sender = User.objects.get(pk=request.user.id)
        sender_username=sender.username
        sent_emails = Amail.objects.filter(sender_email__username=sender_username)

        return render(request, "main/sent.html", {"sent_emails": sent_emails})


class AmailDetail(DetailView):
    model = Amail


def email_detail_for_cc(request, email_id):
    email = Amail.objects.get(id=email_id)
    return render(request, "main/email_detail_for_cc.html", {'email': email})


def trash(request, email_id):
    email = Amail.objects.get(id=email_id)
    email.is_trash=True
    email.save(force_update=True) # for update object with new value
    return HttpResponseRedirect("/main/personal_page/")


def trash_box(request):
    deleted_emails = Amail.objects.filter(is_trash=True)  # from all email Give me deleted emails
    if request.method == 'GET':

        return render(request, "main/trash.html", {'deleted_emails': deleted_emails})
    elif request.method == 'POST':

        deleted_emails.delete()


class NewContact(LoginRequiredMixin, View):
    def get(self, request):
        form = NewContactForm()
        return render(request, "main/new_contact.html", {'form': form})

    def post(self, request):
        form = NewContactForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=request.user.id)
            new_contact = Contacts(user=user,
                                   email=form.cleaned_data['email'],
                                   name=form.cleaned_data['name'],
                                   phone_number=form.cleaned_data['phone_number'],
                                   other_email=form.cleaned_data['other_email'],
                                   birth_date=form.cleaned_data['birth_date'])
            new_contact.save()
            return HttpResponseRedirect("/main/personal_page")
        else:
            HttpResponse(f"faild {form.errors}")


class ContactList(LoginRequiredMixin, View):
    def get(self, request):
        user =User.objects.get(pk=request.user.id)
        user_name =user.username

        contacts = Contacts.objects.filter(user=user)
        return render(request,'main/contact_list.html',{'contacts':contacts})
