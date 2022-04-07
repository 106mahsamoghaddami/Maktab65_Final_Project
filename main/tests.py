from django.test import TestCase
from django.urls import reverse
from .models import *
import json
from django.utils import timezone


# Create your tests here.
class TestViews(TestCase):
    def setUp(self):
        User.objects.create(first_name='Jani', last_name='Bob', birth_date=timezone.now().date(), gender='M',
                            country='usa',
                            phone_number='986451234', email='jani123@gmail.com', recovery='email', is_verified=True,
                            username="jani@mahsa.com", password='jani1234')

        User.objects.create(first_name='Benjamin', last_name='losi', birth_date=timezone.now().date(), gender='M',
                            country='usa', phone_number='987771234', email='benjamin@yahoo.com', recovery='email',
                            is_verified=False,
                            username='benjamin@mahsa.com', password="benjamin1234")

    def test_login(self):
        data = {'username': "jani@mahsa.com", 'password': 'jani1234'}
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)

    def test_send_email(self):
        login = self.client.login(username="jani@mahsa.com",password='jani1234')
        user1_id = User.objects.get(first_name='Jani').id
        user2_id = User.objects.get(first_name='Benjamin').id
        email_data ={'receiver_email':user2_id,'cc':user2_id,'bcc':user1_id,
                     'subject':'test module','text':'this text is from test.py module','file':'',
                     'is_sent':True,'signature':' Sincerely yours Mahsa'}
        response = self.client.post(reverse('SendNewEmail'), email_data)
        self.assertEqual(response.status_code,200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username="jani@mahsa.com", password='jani1234')
        response = self.client.get(reverse('PersonalPage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,"main/personal_page.html")

    def test_detail(self):
        pass