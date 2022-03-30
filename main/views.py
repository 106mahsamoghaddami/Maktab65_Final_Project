import csv

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from .forms import SignUpForm, SendNewEmailForm, NewContactForm, ReplyForm, ForwardForm, NewCategoryForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User, Amail, Contacts, Category
from django.contrib.auth.decorators import login_required
from Final_Maktab65_project import settings
import json
from django.http import JsonResponse


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
        if "submit" in request.POST:

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
                                                 is_sent=True,
                                                 signature=form.cleaned_data['signature']
                                                 )

                new_email.receiver_email.add(receiver_id)
                new_email.cc.add(cc_id)
                new_email.bcc.add(bcc_id)
                new_email.save()

                messages.success(request, f"email send successfully to {receiver} and others")

                return HttpResponseRedirect("/main/personal_page")
        elif "draft" in request.POST:
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
                                                 is_sent=False,
                                                 signature=form.cleaned_data['signature']

                                                 )

                new_email.receiver_email.add(receiver_id)
                new_email.cc.add(cc_id)
                new_email.bcc.add(bcc_id)
                new_email.save()

                messages.success(request, f"email saved successfully in draft box")

                return HttpResponseRedirect("/main/personal_page")


class Inbox(LoginRequiredMixin, View):
    # from emails give me that emails receivers and cc and bcc is my user name(login user)
    def get(self, request):
        receiver = User.objects.get(pk=request.user.id)
        inbox_emails1 = []
        inbox_emails2 = []
        inbox_emails3 = []

        receiver_id = receiver.id
        inbox1 = Amail.objects.filter(receiver_email__id=receiver_id)
        inbox2 = Amail.objects.filter(cc__id=receiver_id)
        inbox3 = Amail.objects.filter(bcc__id=receiver_id)
        # i don't want show deleted emails and draft emails in inbox
        [inbox_emails1.append(email1) for email1 in inbox1 if
         email1.is_trash == False and email1.is_sent == True and email1.is_filter == False]
        [inbox_emails2.append(email2) for email2 in inbox2 if
         email2.is_trash == False and email2.is_sent == True and email2.is_filter == False]
        [inbox_emails3.append(email3) for email3 in inbox3 if
         email3.is_trash == False and email3.is_sent == True and email3.is_filter == False]

        return render(request, "main/personal_page.html", {"inbox_emails1": inbox_emails1,
                                                           "inbox_emails2": inbox_emails2,
                                                           "inbox_emails3": inbox_emails3})


class SentBox(LoginRequiredMixin, View):
    # from emails give me that emails sender is my user name(login user)
    def get(self, request):
        sent_emails = []
        sender = User.objects.get(pk=request.user.id)
        sender_username = sender.username
        sent = Amail.objects.filter(sender_email__username=sender_username)
        [sent_emails.append(email) for email in sent if
         email.is_trash == False and email.is_sent == True and email.is_filter == False]

        return render(request, "main/sent.html", {"sent_emails": sent_emails})


class AmailDetail(LoginRequiredMixin, View):
    def get(self, request, email_id):
        email = Amail.objects.get(id=email_id)
        user = User.objects.get(pk=request.user.id)
        user_labels = []
        try:
            for label in Category.objects.all():
                if label.owner == user:
                    user_labels.append(label)

            return render(request, "main/amail_detail.html", {'email': email, 'user_labels': user_labels})
        except:
            print("You have not defined any labels")
            return HttpResponseRedirect("/main/category_list/")

    def post(self, request, email_id):
        user = User.objects.get(pk=request.user.id)
        email = Amail.objects.get(id=email_id)
        choice_label = request.POST['label']

        for cat in Category.objects.all():

            if str(cat) == choice_label and cat.owner == user:
                email.label = cat
                email.save(force_update=True)

        messages.success(request, f"assigned {choice_label} label for your {email} email ")
        return HttpResponseRedirect("/main/category_list/")


def email_detail_for_cc(request, email_id):
    email = Amail.objects.get(id=email_id)
    return render(request, "main/email_detail_for_cc.html", {'email': email})


class ReplyEmail(LoginRequiredMixin, View):

    def post(self, request, id):
        email = Amail.objects.get(pk=id)
        receiver = email.receiver_email.all()
        receiver = receiver[0]

        for user in User.objects.all():
            if user == receiver:
                receiver_id = user.id

        sender = User.objects.get(pk=request.user.id)
        form = ReplyForm(request.POST, request.FILES)
        if form.is_valid():
            # reply_mail = form.save(commit=False)
            new_mail = Amail.objects.create(sender_email=sender,
                                            subject=form.cleaned_data['subject'],
                                            text=form.cleaned_data['text'],
                                            file=form.cleaned_data['file'],
                                            is_sent=True,
                                            signature=form.cleaned_data['signature'],
                                            replied_email=email

                                            )
            new_mail.receiver_email.add(receiver_id)
            new_mail.save()
            messages.success(request, f"email send successfully ")
            return HttpResponseRedirect("/main/sent/")

    def get(self, request, id):
        form = ReplyForm()
        email = Amail.objects.get(pk=id)
        return render(request, "main/reply.html", {'form': form, 'email': email})


class ForwardEmail(LoginRequiredMixin, View):
    def get(self, request, id):
        selected_email = Amail.objects.get(pk=id)
        form = ForwardForm()
        return render(request, "main/forward.html", {'form': form, 'email': selected_email})

    def post(self, request, id):
        sender = User.objects.get(pk=request.user.id)  # for set sender
        selected_email = Amail.objects.get(pk=id)  # for set subject and text from main email

        form = ForwardForm(request.POST, request.FILES)

        if form.is_valid():

            receiver = form.cleaned_data['receiver_email']
            cc = form.cleaned_data['cc']
            bcc = form.cleaned_data['bcc']

            for user in User.objects.all():
                if user == receiver[0]:
                    receiver_id = user.id
            for user1 in User.objects.all():
                if user1 == cc[0]:
                    cc_id = user1.id
            for user2 in User.objects.all():
                if user2 == bcc[0]:
                    bcc_id = user2.id
            email = Amail.objects.create(sender_email=sender,
                                         subject=request.POST['subject'],
                                         text=request.POST['text'],
                                         file=request.POST['file'],
                                         signature=form.cleaned_data['signature'],
                                         is_sent=True
                                         )
            email.receiver_email.add(receiver_id)
            email.cc.add(cc_id)
            email.bcc.add(bcc_id)
            email.save()
        messages.success(request, f"email send successfully ")
        return HttpResponseRedirect("/main/sent/")


def trash(request, email_id):
    email = Amail.objects.get(id=email_id)
    email.is_trash = True
    email.save(force_update=True)  # for update object with new value
    messages.success(request, f"email trashed successfully ")
    return HttpResponseRedirect("/main/personal_page/")


class TrashBox(LoginRequiredMixin, View):
    """ in this part i need to get all user's email that is_trash == True for show in trash box:
    so first I get all emails with a username that is logged in as a receiver and sender
    after that I select the deleted emails from among them and put them to the list  deleted_emails
     """

    def get(self, request):
        deleted_emails = []
        user = User.objects.get(pk=request.user.id)  # that user is logged in system

        # user 's email that user is sender
        check_sender_user = Amail.objects.filter(sender_email_id=user.id)
        for email in check_sender_user:
            if email.is_trash:
                deleted_emails.append(email)

        # user 's email that user is receiver
        check_user_emails1 = Amail.objects.filter(receiver_email__id=user.id)
        for email1 in check_user_emails1:
            if email1.is_trash:
                deleted_emails.append(email1)

        # user 's email that user is cc
        check_cc_user = Amail.objects.filter(cc__id=user.id)
        for email2 in check_cc_user:
            if email2.is_trash:
                deleted_emails.append(email2)

        # user 's email that user is bcc
        check_bcc_user = Amail.objects.filter(bcc__id=user.id)
        for email3 in check_bcc_user:
            if email3.is_trash:
                deleted_emails.append(email3)

        return render(request, "main/trash.html", {'deleted_emails': deleted_emails})

    def post(self, request):

        TrashBox.deleted_emails.delete()  # Publication.objects.filter(title__startswith='Science').delete()


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
            messages.success(request, f"new contact added   successfully ")
            return HttpResponseRedirect("/main/contact_list/")
        else:
            HttpResponse(f"faild {form.errors}")


class ContactList(LoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        user_name = user.username

        contacts = Contacts.objects.filter(user=user)
        return render(request, 'main/contact_list.html', {'contacts': contacts})


class DetailContacts(View):
    def get(self, request, id):
        contact = Contacts.objects.get(pk=id)
        return render(request, 'main/detailcontacts.html', {'contact': contact})


class ExportCsv(LoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        contacts = Contacts.objects.all().filter(user_id=user.id)  # give me just contact of this user hase log in
        response = HttpResponse('text/csv')
        response['Content-Disposition'] = 'attachment; filename=contact.csv'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Owner', 'Email', 'Name', 'Phone Number', 'Other email', 'Birth_Date'])
        cont = contacts.values_list('id', 'user', 'email', 'name', 'phone_number', 'other_email', 'birth_date')
        for c in cont:
            writer.writerow(c)
        return response


def search(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        emails = Amail.objects.filter(Q(sender_email=request.user.id) | Q(receiver_email=request.user.id),
                                      Q(receiver_email__username__icontains=search_str) |
                                      Q(cc__username__istartswith=search_str, sender_email=request.user) |
                                      Q(bcc__username__istartswith=search_str, sender_email=request.user) |
                                      Q(subject__icontains=search_str) | Q(text__icontains=search_str) |
                                      Q(label__amail__text__icontains=search_str))

        data = emails.values()

        # print(data)
        return JsonResponse(list(data), safe=False)


def search_contact(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        contact = Contacts.objects.filter(Q(name__icontains=search_str, user=request.user.id) |
                                          Q(email__icontains=search_str, user=request.user.id) |
                                          Q(phone_number__icontains=search_str, user=request.user.id) |
                                          Q(birth_date__istartswith=search_str))

        data = contact.values()
        # print(data)
        return JsonResponse(list(data), safe=False)


class UpdateContacts(LoginRequiredMixin, View):
    form_class = NewContactForm

    def setup(self, request, *args, **kwargs):
        self.contact_instance = get_object_or_404(Contacts, pk=kwargs['id'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        contact = self.contact_instance
        if not contact.user == request.user:
            messages.error(request, 'you cant update this contact', 'danger')
            return redirect('main:ContactList')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        contact = self.contact_instance
        contact_id = contact.id
        print(contact_id)

        form = self.form_class(instance=contact)
        return render(request, 'main/update_contact.html', {'form': form})

    def post(self, request, *args, **kwargs):
        contact = self.contact_instance
        form = self.form_class(request.POST, instance=contact)
        if form.is_valid():
            print("salam")
            new_contact = form.save(commit=False)
            print(f"new_contact :{new_contact}")
            cd = form.cleaned_data
            print(cd)
            # email = get_object_or_404(User, username=cd['email'])
            owner = request.user
            new_contact.user = owner
            new_contact.save(force_update=True)
            messages.success(request, 'you updated this post', 'success')

            return HttpResponseRedirect("/main/contact_list/")


class DeleteContact(LoginRequiredMixin, View):
    def get(self, request, id):
        selected_contact = Contacts.objects.get(pk=id)
        user = User.objects.get(pk=request.user.id)  # that user is logged in system
        print(user)
        print(selected_contact)
        if selected_contact.user == user:
            selected_contact.delete()
            messages.success(request, "contact delete successfully")
            return HttpResponseRedirect("/main/contact_list/")


class DraftBox(LoginRequiredMixin, View):
    """ in this part i need to get all user's email that is_sent == True for show in draft box:
    so first I get all emails with a username that is logged in as a  sender
    after that I select the draft emails from among them and put them to the list  draft_emails
     """

    def get(self, request):
        draft_emails = []
        user = User.objects.get(pk=request.user.id)  # that user is logged in system

        # user 's email that user is sender
        check_sender_user = Amail.objects.filter(sender_email_id=user.id)
        for email in check_sender_user:
            if email.is_sent == False:
                draft_emails.append(email)

        return render(request, "main/draft_box.html", {'draft_emails': draft_emails})


def draft_detail(request, email_id):
    email = Amail.objects.get(id=email_id)

    return render(request, "main/draft_detail.html", {'email': email})


class ManageDrafts(LoginRequiredMixin, View):
    def get(self, request, email_id):
        email = Amail.objects.get(id=email_id)

        return render(request, "main/send_new_email_form_draft.html", {'email': email})

    def post(self, request, email_id):
        user = User.objects.get(pk=request.user.id)

        for user in User.objects.all():
            if user.username == request.POST['receiver']:
                receiver_id = user.id
        for user1 in User.objects.all():
            if user1.username == request.POST['cc']:
                cc_id = user1.id
        for user2 in User.objects.all():
            if user2.username == request.POST['bcc']:
                bcc_id = user2.id
        print(request.POST)
        if "submit" in request.POST:

            email = Amail.objects.get(id=email_id)
            print(email)
            print(email.receiver_email)
            email.receiver_email.add(receiver_id)
            email.cc.add(cc_id)
            email.bcc.add(bcc_id)

            email.subject = request.POST['subject']
            email.text = request.POST['text']
            email.file = request.POST['file']
            email.is_sent = True
            email.save(force_update=True)
            messages.success(request, f"email send successfully ")
            return HttpResponseRedirect("/main/personal_page/")

        elif "draft" in request.POST:
            mail = Amail.objects.get(id=email_id)
            mail.receiver_email.add(receiver_id)
            mail.cc.add(cc_id)
            mail.bcc.add(bcc_id)
            mail.subject = request.POST['subject']
            mail.text = request.POST['text']
            mail.file = request.POST['file']
            mail.is_sent = False
            mail.save(force_update=True)
            return HttpResponseRedirect("/main/personal_page/")

            return HttpResponseRedirect("/main/draft_box/")


def make_archive(request, mail_id):
    email = Amail.objects.get(id=mail_id)
    email.is_archive = True
    email.save(force_update=True)  # for update object with new value
    return HttpResponseRedirect("/main/personal_page/")


def unarchive(request, mail_id):
    if request.method == 'GET':
        email = Amail.objects.get(id=mail_id)
        return render(request, "main/unarchive.html", {'email': email})
    if request.method == 'POST':
        email = Amail.objects.get(id=mail_id)
        email.is_archive = False
        email.save(force_update=True)  # for update object with new value
        return HttpResponseRedirect("/main/archive_box/")


class ArchiveBox(LoginRequiredMixin, View):
    """ in this part i need to get all user's email that is_archive == True for show in archive box:
    so first I get all emails with a username that is logged in as a receiver and sender
    after that I select the archives emails from among them and put them to the list  archive_emails
     """

    def get(self, request):
        archive_emails = []
        user = User.objects.get(pk=request.user.id)  # that user is logged in system

        # user 's email that user is sender
        check_sender_user = Amail.objects.filter(sender_email_id=user.id)
        for email in check_sender_user:
            if email.is_archive:
                archive_emails.append(email)

        # user 's email that user is receiver
        check_user_emails1 = Amail.objects.filter(receiver_email__id=user.id)
        for email1 in check_user_emails1:
            if email1.is_archive:
                archive_emails.append(email1)

        # user 's email that user is cc
        check_cc_user = Amail.objects.filter(cc__id=user.id)
        for email2 in check_cc_user:
            if email2.is_archive:
                archive_emails.append(email2)

        # user 's email that user is bcc
        check_bcc_user = Amail.objects.filter(bcc__id=user.id)
        for email3 in check_bcc_user:
            if email3.is_archive:
                archive_emails.append(email3)

        return render(request, "main/archive_box.html", {'archive_emails': archive_emails})


class NewCategory(LoginRequiredMixin, View):
    def get(self, request):
        forms = NewCategoryForm
        return render(request, "main/new_category.html", {'forms': forms})

    def post(self, request):
        form = NewCategoryForm(request.POST)
        if form.is_valid():
            user = User.objects.get(pk=request.user.id)
            new_category = Category(owner=user,
                                    name=form.cleaned_data['name'])
            new_category.save()
            messages.success(request, f"new label created successfully ")

            return HttpResponseRedirect("/main/category_list/")


class ShowCategory(LoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        print(user)
        all_category = []
        # all_category = Category.objects.get(owner=user)
        for cat in Category.objects.all():
            if cat.owner == user:
                all_category.append(cat)
        if all_category:
            return render(request, "main/category_list.html", {'all_category': all_category})
        else:
            message = f" Dear {user.first_name} you have not created any labels before"
            return render(request, "main/category_list.html", {'message': message})


class EmailsOfCategory(LoginRequiredMixin, View):
    def get(self, request, cat_id):

        emails = []
        user = User.objects.get(pk=request.user.id)  # that user is logged in system

        # user 's email that user is sender
        check_sender_user = Amail.objects.filter(sender_email_id=user.id)
        for email in check_sender_user:
            if email.label_id == cat_id:
                emails.append(email)

        # user 's email that user is receiver
        check_user_emails1 = Amail.objects.filter(receiver_email__id=user.id)
        for email1 in check_user_emails1:
            if email1.label_id == cat_id:
                emails.append(email1)

        # user 's email that user is cc
        check_cc_user = Amail.objects.filter(cc__id=user.id)
        for email2 in check_cc_user:
            if email2.label_id == cat_id:
                emails.append(email2)

        # user 's email that user is bcc
        check_bcc_user = Amail.objects.filter(bcc__id=user.id)
        for email3 in check_bcc_user:
            if email3.label_id == cat_id:
                emails.append(email3)
        if emails:
            return render(request, "main/emails_of_spacial_category.html", {'emails': emails, 'label_id': cat_id})
        else:
            message = f" You have not added any emails to this label yet"
            return render(request, "main/emails_of_spacial_category.html", {'message': message, 'label_id': cat_id})


class DeleteLabel(LoginRequiredMixin, View):
    def get(self, request, id):
        selected_label = Category.objects.get(pk=id)
        user = User.objects.get(pk=request.user.id)  # that user is logged in system

        if selected_label.owner == user:
            selected_label.delete()
            messages.success(request, f"label delete  successfully ")

            return HttpResponseRedirect("/main/category_list/")


class Filter(LoginRequiredMixin, View):
    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        user_labels = []
        try:
            for label in Category.objects.all():
                if label.owner == user:
                    user_labels.append(label)

            return render(request, "main/filter.html", {'user_labels': user_labels})
        except:

            return HttpResponse("page not find")

    """user can filter emails by subject and text or username 
    so we have 2 condition to know this filter is by text or user name """

    def post(self, request):

        if request.POST['choice'] == 'subject':  # filter by subject and text
            try:

                user = User.objects.get(pk=request.user.id)

                user_id = user.id
                all_emails = Amail.objects.filter(Q(receiver_email__id=user_id) | Q(sender_email=request.user.id))
                for email in all_emails:
                    if request.POST['filter_word'] in email.subject or request.POST['filter_word'] in email.text:
                        choice_label = request.POST['label']

                        for cat in Category.objects.all():

                            if str(cat) == choice_label and cat.owner == user:
                                email.label = cat
                                email.is_filter = True

                                email.save(force_update=True)

                messages.success(request, f"email filtered successfully ")
                return HttpResponseRedirect("/main/category_list/")


            except:
                messages.warning(request, f" some thing is wrong try again  !!")
                return HttpResponseRedirect("/main/filter/")


        elif request.POST['choice'] == 'username':  # filter by username
            try:
                if request.POST['filter_word'] != "":
                    user = User.objects.get(pk=request.user.id)

                    user_id = user.id
                    all_emails = Amail.objects.filter(Q(receiver_email__id=user_id) | Q(sender_email=request.user.id))
                    # from all emails we need them receiver or sender is login user
                    for email in all_emails:

                        if str(email.sender_email) == request.POST['filter_word']:

                            choice_label = request.POST['label']

                            for cat in Category.objects.all():

                                if str(cat) == choice_label and cat.owner == user:
                                    email.label = cat
                                    email.is_filter = True

                                    email.save(force_update=True)
                    messages.success(request, f"email filtered successfully ")
                    return HttpResponseRedirect("/main/category_list/")
                else:
                    messages.warning(request, f" inter words for search and filter  !!")
            except:
                messages.warning(request, f" some thing is wrong try again  !!")
                return HttpResponseRedirect("/main/filter/")
