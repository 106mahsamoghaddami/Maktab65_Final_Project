from . import views
from django.urls import path

urlpatterns = [
    path('', views.home, name='home'),
    path("register/", views.signup, name="signup"),
    path('activate/<uidb64>/<token>/', views.activate_mail, name="activate"),
    path('login/', views.Login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('personal_page/', views.PersonalPage.as_view(), name='PersonalPage'),
    path('send_email/', views.SendNewEmail.as_view(), name='SendNewEmail'),
    path('inbox/', views.Inbox.as_view(), name='Inbox'),
    path('sent/', views.Sent.as_view(), name='Sent'),
    path('email_detail/<int:pk>', views.AmailDetail.as_view(), name='EmailDetail'),
    path('email_detail_for_cc/<int:email_id>', views.email_detail_for_cc, name='EmailDetailCC'),
    path('trash/<int:email_id>', views.trash, name='trash'),
    path('trash_box/', views.trash_box, name='trash_box'),
    path('new_contact/', views.NewContact.as_view(), name='NewContact'),
    path('contact_list/', views.ContactList.as_view(), name='ContactList'),


]



