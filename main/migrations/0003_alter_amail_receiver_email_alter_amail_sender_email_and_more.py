# Generated by Django 4.0.2 on 2022-03-10 21:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_amail_is_read_amail_is_sent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amail',
            name='receiver_email',
            field=models.ManyToManyField(blank=True, related_name='receive_emails', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='amail',
            name='sender_email',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_emails', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('owner', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='category', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='amail',
            name='label',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.category'),
        ),
    ]
