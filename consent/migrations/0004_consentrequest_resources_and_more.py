# Generated by Django 4.1.5 on 2023-02-23 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consent', '0003_consentrequest_consentid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='consentrequest',
            name='resources',
            field=models.JSONField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='consentrequest',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]