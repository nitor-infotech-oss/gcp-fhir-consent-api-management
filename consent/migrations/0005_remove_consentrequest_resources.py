# Generated by Django 4.1.5 on 2023-02-24 09:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('consent', '0004_consentrequest_resources_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consentrequest',
            name='resources',
        ),
    ]
