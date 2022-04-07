from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import *
from .serializers import *



@api_view()
@permission_classes([IsAuthenticated, ])
def detail_contact(request):
    contact = Contacts.objects.filter(user=request.user)
    ser_data = ContactUserSerializer(contact, many=True)
    return Response(ser_data.data)


@api_view()
@permission_classes([IsAuthenticated, ])
def detail_email(request):
    email = Amail.objects.filter(sender_email=request.user)
    ser_data = EmailSerializer(email, many=True)
    return Response(ser_data.data)
