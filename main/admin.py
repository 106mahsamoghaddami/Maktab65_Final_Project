from django.contrib import admin
from .models import User, Amail, Contacts, Category
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Q
from django.db.models.functions import TruncDay, TruncMonth
from django.http import JsonResponse
from django.urls import path
import json
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages


def sizify(value):
    """
    Simple kb/mb/gb size:
    """
    # value = ing(value)
    if value < 512000:
        value = value / 1024.0
        ext = 'kb'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'mb'
    else:
        value = value / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(value, 2)), ext)


# @admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username', 'sent_emails', 'received_emails', 'strange_used')

    ordering = ('-date_joined',)

    @staticmethod
    def sent_emails(obj):
        from django.db.models import Avg
        sent = Amail.objects.filter(sender_email=obj).count()
        return sent

    @staticmethod
    def received_emails(obj):
        received = Amail.objects.filter(receiver_email=obj).count()
        return received

    @staticmethod
    def strange_used(obj):
        emails_file = Amail.objects.filter(Q(sender_email=obj) | Q(receiver_email=obj)).exclude(file=None,
                                                                                                file__isnull=False)
        total = sum(int(objects.file_size) for objects in emails_file if objects.file_size)
        total = sizify(total)
        return total

    # Inject chart data on page load in the ChangeList view
    def changelist_view(self, request, extra_context=None):
        email_file = Amail.objects.filter(file__isnull=False).exclude(file='')
        usernames = []
        file_data = []
        for email in email_file:
            usernames.append(User.objects.get(pk=email.sender_email.id))
            usernames = set(usernames)
            usernames = list(usernames)
        for user in set(usernames):
            files_user = email_file.filter(sender_email=user)
            total = sum(int(objects.file_size) for objects in files_user if objects.file_size)
            # total = sizify(total)
            file_data.append({"user": user.username, "user_size": total})
            print(file_data)
            print("*" * 40)


        chart_data = self.chart_data()
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json,"file_data": file_data}
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path("chart_data/", self.admin_site.admin_view(self.chart_data_endpoint))
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls

    # JSON endpoint for generating chart data that is used for dynamic loading
    # via JS.
    def chart_data_endpoint(self, request):
        chart_data = self.chart_data()
        return JsonResponse(list(chart_data), safe=False)

    def chart_data(self):
        return (
            User.objects.annotate(date=TruncMonth("date_joined"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )


""" for show  emails of a month"""


class AmailAdmin(admin.ModelAdmin):
    list_display = ("id", "sender_email", "receiver_email")
    ordering = ("-date_time",)

    @staticmethod
    def receiver_email(obj):
        receiver = Amail.objects.filter(receiver_email__username=obj)

        return receiver

    # Inject chart data on page load in the ChangeList view
    def changelist_view(self, request, extra_context=None):
        chart_data = self.chart_data()
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path("chart_data/", self.admin_site.admin_view(self.chart_data_endpoint))
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls

    # JSON endpoint for generating chart data that is used for dynamic loading
    # via JS.
    def chart_data_endpoint(self, request):
        chart_data = self.chart_data()
        return JsonResponse(list(chart_data), safe=False)

    def chart_data(self):
        return (
            Amail.objects.annotate(date=TruncDay("date_time"))  # after check change it to TruncMonth
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )


class CategoryAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ['owner','name']

    def add_view(self, request ):
        if request.method == 'POST':
            try:
                users = User.objects.all()
                for user in users:
                    Category.objects.create(owner_id=user.pk, name=request.POST.get('name'))

                return HttpResponseRedirect("/admin/main/category/")
            except Exception as e:
                messages.error(request, 'this label exist', extra_tags='error')
                return HttpResponseRedirect("/admin/main/category/add/")
        return super(CategoryAdmin, self).add_view(request)


admin.site.register(User, UserAdmin)
admin.site.register(Amail, AmailAdmin)
admin.site.register(Contacts)
admin.site.register(Category,CategoryAdmin)
