from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length = 20, unique = True)
    
    def __str__(self):
        return f'{self.name}'


class Listing(models.Model):
    title = models.CharField(max_length = 60, blank = False)
    description = models.TextField(blank = True, default = '')
    picture = models.URLField(blank = True, default = '')
    price = models.DecimalField(max_digits = 11, decimal_places = 2, blank = False)
    posted_time = models.DateTimeField(auto_now_add = True)
    active = models.BooleanField(default = True)
    seller = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'sell_listings',
        null = True,
        default = None,
        )
    categories = models.ManyToManyField(
        Category,
        related_name = 'listings',
        default = None,
        )
    watchers = models.ManyToManyField(
        User,
        related_name = 'watchlist',
        default = None,
        )
    
    def __str__(self):
        trunc_title = self.title[20:] + '...' if len(self.title) > 20 else self.title
        return f'Item #{self.id} : {trunc_title}'


class Bid(models.Model):
    price = models.DecimalField(max_digits = 11, decimal_places = 2)
    posted_time = models.DateTimeField(auto_now_add = True)
    buyer = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'bids',
        null = True,
        default = None,
        )
    listing = models.ForeignKey(
        Listing,
        on_delete = models.CASCADE,
        related_name = 'bids',
        null = True,
        default = None,
        )
    
    def __str__(self):
        return f'{self.listing} || Bid #{self.id}'


class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = 'comments',
        null = True,
        default = None,
        )
    listing = models.ForeignKey(
        Listing,
        on_delete = models.CASCADE,
        related_name = 'comments',
        null = True,
        default = None,
        )
    
    def __str__(self):
        return f'{self.listing} || Comment #{self.id}'

