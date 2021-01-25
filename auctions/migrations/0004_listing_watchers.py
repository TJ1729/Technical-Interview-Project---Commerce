# Generated by Django 3.0.8 on 2020-07-13 18:36

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20200713_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='watchers',
            field=models.ManyToManyField(blank=True, default='', related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]
