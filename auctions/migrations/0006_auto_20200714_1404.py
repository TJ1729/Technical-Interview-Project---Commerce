# Generated by Django 3.0.8 on 2020-07-14 13:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20200714_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='categories',
            field=models.ManyToManyField(default=None, null=True, related_name='listings', to='auctions.Category'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='watchers',
            field=models.ManyToManyField(default=None, null=True, related_name='watchlist', to=settings.AUTH_USER_MODEL),
        ),
    ]
