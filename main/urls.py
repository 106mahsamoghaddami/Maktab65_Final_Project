from . import views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('', views.home, name='home'),
    path("register/", views.signup, name="signup"),
    path('activate/<uidb64>/<token>/', views.activate_mail, name="activate"),
    path('login/', views.Login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('personal_page/', views.PersonalPage.as_view(), name='PersonalPage'),
    path('send_email/', views.SendNewEmail.as_view(), name='SendNewEmail'),
    path('inbox/', views.Inbox.as_view(), name='Inbox'),
    path('sent/', views.SentBox.as_view(), name='Sent'),
    path('email_detail/<int:email_id>', views.AmailDetail.as_view(), name='EmailDetail'),
    path('email_detail_for_cc/<int:email_id>', views.email_detail_for_cc, name='EmailDetailCC'),
    path('reply_email/<int:id>', views.ReplyEmail.as_view(), name='reply'),
    path('forward_email/<int:id>', views.ForwardEmail.as_view(), name='forward'),
    path('trash/<int:email_id>', views.trash, name='trash'),
    path('trash_box/', views.TrashBox.as_view(), name='TrashBox'),
    path('new_contact/', views.NewContact.as_view(), name='NewContact'),
    path('contact_list/', views.ContactList.as_view(), name='ContactList'),
    path('contact_detail/<int:id>', views.DetailContacts.as_view(), name='ContactDetail'),
    path('exportcsv/', views.ExportCsv.as_view(),name='exportcsv'),
    path('updatecontacts/<int:id>', views.UpdateContacts.as_view(), name='UpdateContacts'),
    path('deletecontacts/<int:id>', views.DeleteContact.as_view(), name='DeleteContacts'),
    path('draft_box/', views.DraftBox.as_view(), name='DraftBox'),
    path('draft_detail/<int:email_id>', views.draft_detail, name='DraftDetail'),
    path('manage_drafts/<int:email_id>', views.ManageDrafts.as_view(), name='ManageDrafts'),
    path('make_archive/<int:mail_id>', views.make_archive, name='make_archive'),
    path('make_unarchive/<int:mail_id>', views.unarchive, name='un_archive'),
    path('archive_box/', views.ArchiveBox.as_view(), name='ArchiveBox'),
    path('new_category/', views.NewCategory.as_view(), name='NewCategory'),
    path('category_list/', views.ShowCategory.as_view(), name='ShowAllCategory'),
    path('emails_of_category/<int:cat_id>', views.EmailsOfCategory.as_view(), name='EmailOfCategory'),
    path('delete_category/<int:id>', views.DeleteLabel.as_view(), name='DeleteLabel'),
    path('search_email/', csrf_exempt(views.search), name='search'),
    path('search_contact/', csrf_exempt(views.search_contact), name='search_contact'),
    path('filter/', views.Filter.as_view(), name='search_contact'),





]



