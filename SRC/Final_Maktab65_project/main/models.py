from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string


class User(AbstractUser):
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    birth_date = models.DateTimeField(null=True)
    gender_choice = [
        ('F', 'Female'),
        ('M', 'Man'),
        ('U', 'Unknown'),

    ]
    gender = models.CharField(max_length=1, choices=gender_choice, null=True)
    country = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    recovery_choice = [
        ('phone', 'phone'),
        ('email', 'email'),
    ]
    recovery = models.CharField(max_length=5, choices=recovery_choice)

    is_verified = models.BooleanField(default=False,
                                      null=True)  # this field added after migrate  so null=True is  for old data

    def __str__(self):
        return self.username


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    # instance is the user object which has just been created
    if created:  # check if the user has been created
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        subject = "Account Varification"
        html_message = f"""
                        <div>

                    <h3>Hi {instance.first_name},</h3> 

                    <p>As a form of avoiding unrealistic and unserious users, we have to ensure email confirmation. 
                    Please click on the link to confirm your registration</p>

                    <a href=\"http://localhost:8000/activate/{uid}/{token}\" style="color:white; text-decoration: none;border-radius: 25px; background-color: #754C28; padding: 7px 25px;"> <strong>Verify Email<strong></a>

                    <br><br>If you think, it's not you, then just ignore this email. Thank you.  

                </div>"""

        email_content = ""

        try:
            send_mail(subject, email_content, "senderemail@gmail.com", [instance.email], fail_silently=False,
                      html_message=html_message)
        except BadHeaderError:
            pass


class Contacts(models.Model):
    user = models.ManyToManyField(User)  # this contact is for user and an user have many contacts
    email = models.EmailField()
    name = models.CharField(max_length=70)
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True)
    other_email = models.EmailField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f" {self.name} : {self.email}"


class Amail(models.Model):
    sender_email = models.ForeignKey(User, on_delete=models.CASCADE)  # an user can send many email
    receiver_email = models.ManyToManyField(Contacts)  # a person who received email
    cc = models.EmailField(null=True, blank=True)
    bcc = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    text = models.TextField(max_length=200, null=True, blank=True)
    file = models.FileField(null=True, blank=True)

    def __str__(self):
        return f"{self.sender_email} send email to {self.receiver_email} by {self.subject} subject"
