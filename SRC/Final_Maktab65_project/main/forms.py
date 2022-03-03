from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User,Amail ,Contacts


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        # Add fields we will be collecting info for
        fields = ['first_name', 'last_name', 'birth_date', 'gender', 'country',
                  'phone_number', 'email', 'recovery', 'username', 'password']

    # DO form cleanig here
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username is not available')
        elif '@' in username or username[:-4] == '.com':
            raise ValidationError("please enter your username without @ and .com ")
        username = str(username)+"@mahsa.com"
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email not available for use")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # check password length
        if len(password) < 8:
            raise ValidationError("Password can't be less than 8 characters")
        # check for number and letters is password
        if password.isalpha() or password.isnumeric():
            raise ValidationError("Password should contains both letters and numbers")

        return password

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number == "":
            raise ValidationError("phone number can't be empty")
        else:
            if User.objects.filter(phone_number=phone_number):
                raise ValidationError("phone number not available for use")
        return phone_number


class SendNewEmailForm(forms.ModelForm):
    class Meta:
        model = Amail
        fields = ['receiver_email', 'cc', 'bcc', 'subject', 'text', 'file']


class NewContactForm(forms.ModelForm):
    class Meta:
        model = Contacts
        fields = ['email', 'name', 'phone_number', 'other_email', 'birth_date']
