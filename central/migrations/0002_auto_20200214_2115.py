# Generated by Django 2.1.9 on 2020-02-14 21:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='participants',
            field=models.ManyToManyField(blank=True, null=True, related_name='participants', to=settings.AUTH_USER_MODEL, verbose_name='Participants'),
        ),
    ]
