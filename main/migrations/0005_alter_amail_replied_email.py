# Generated by Django 4.0.2 on 2022-03-17 22:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_amail_replied_email_alter_amail_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amail',
            name='replied_email',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.amail'),
        ),
    ]