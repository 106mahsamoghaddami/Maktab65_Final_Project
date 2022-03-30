# Generated by Django 4.0.2 on 2022-03-17 22:29

from django.db import migrations, models
import main.validators


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_amail_receiver_email_alter_amail_sender_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='amail',
            name='replied_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='amail',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='media/', validators=[main.validators.validate_file_size]),
        ),
    ]