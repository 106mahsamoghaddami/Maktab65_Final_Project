from rest_framework import serializers



class ContactUserSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    birth_date = serializers.DateField()


class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField()
    text = serializers.CharField()
    sender_email = serializers.CharField()
    date_time = serializers.DateTimeField()