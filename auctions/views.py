from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from decimal import Decimal

from .models import *


def index(request):
    # Landing page displays all active listings filtered by category and keyword passed by url parems
    f_listings = Listing.objects.filter(active__exact = True)
    filter_category = request.GET.get("c", None)
    if filter_category is not None:
        f_listings = f_listings.filter(categories__name = filter_category)

    filter_kwd = request.GET.get("q", None)
    if filter_kwd is not None:
        f_listings = f_listings.filter(title__contains = filter_kwd) | f_listings.filter(description__contains = filter_kwd)
    
    ctgry_links = Category.objects.all()
    
    return render(request, "auctions/index.html", {
        "all_listings": f_listings,
        "filter_category": filter_category,
        "filter_kwd": filter_kwd,
        })


@login_required
def watchlist(request):
    f_listings = request.user.watchlist.all()
    f_listings = f_listings.filter(active__exact = True)
    
    filter_category = request.GET.get("c", None)
    if filter_category is not None:
        f_listings = f_listings.filter(categories__name__exact = filter_category)
    
    return render(request, "auctions/index.html", {
        "all_listings": f_listings,
        "filter_category": filter_category,
        "watchlist": True,
        })

# *** This code (lines 46-99) came with the spec - I didn't write it ***
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html", {
            })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html", {
            })
# *** end of code that came with spec ***

def listing(request, id):
    item = Listing.objects.get(pk = id)

    # Find out if this item is in the user's watchlist
    try:
        request.user.watchlist.get(id__exact = item.id)
        w = True
    except:
        w = False
    
    ctgry_links = item.categories.all()
    bids = item.bids.all()
    
    # If there are no bids the page can display the item's -rice set by the seller
    if not bids:
        return render(request, "auctions/listing.html", {
            "item": item,
            "watching": w,
            "ctgry_links": ctgry_links
            })
    else:
        return render(request, "auctions/listing.html", {
            "item": item,
            "watching": w,
            "highest_bid": bids.latest("price"), # Newest bid is the highest
            "ctgry_links": ctgry_links
            })

@login_required
def listeditor(request):
    return render(request, "auctions/itemeditor.html", {
        "categories": Category.objects.all(),
        })

@login_required
def postlisting(request):
    if request.method == "POST":
        
        # Get all the inputs from the form and make sure they're in the right format
        title = request.POST.get("title", None)
        description = request.POST.get("description", "")
        picture = request.POST.get("picture", "")
        price = Decimal( request.POST.get("price", None) )
        seller = request.user
        watchers = request.user
        
        # Save the object
        try:
            newlisting = Listing(title=title, description=description, picture=picture, price=price, seller=seller, watchers=watchers)
            newlisting.save()
            messages.success(request, "Listing posted successfully.")
            return HttpResponseRedirect(reverse("listing", args=(newlisting.id,)))
        except IntegrityError:
            messages.error(request, "Listing must have at least nonempty title and price to be posted.", extra_tags="danger")
        
    else:
        messages.error(request, "(403)Invalid method - please use form provided to create new listings.", extra_tags="danger")
    
    return HttpResponseRedirect(reverse("listeditor"))

@login_required
def postbid(request, id):
    if request.method == "POST":
        
        price = Decimal( request.POST.get("price") )
        item = Listing.objects.get(pk = id)
        buyer = request.user
        
        # Find the minimum allowed bid
        try:
            minbid = item.bids.all().latest("price").price
        except Bid.DoesNotExist:
            minbid = item.price
        
        # Check for user input errors
        if not buyer.is_authenticated:
            messages.error(request, "Must be logged in to bid.", extra_tags="danger")
        elif buyer == item.seller:
            messages.error(request, "Cannot bid on listings you posted.", extra_tags="danger")
        elif price <= minbid:
            messages.error(request, "Bid must be greater than the current highest bid.", extra_tags="danger")
        elif price > 999999.99:
            messages.error(request, "Bid exceeded allowed maximum of £999,999.99.", extra_tags="danger")
        else:
            Bid(price=price, buyer=buyer, listing=item).save()
            messages.success(request, "Bid was posted successfully.")
    else:
        messages.error(request, "(403)Invalid method - please use form provided to post bids.", extra_tags="danger")
    return HttpResponseRedirect(reverse("listing", args=(id,)))

@login_required
def postcomment(request, id):
    if request.method == "POST":
        
        content = request.POST.get("content")
        listing = Listing.objects.get(pk = id)
        user = request.user
        
        newcomment = Comment(content=content, listing=listing, user=user)
        newcomment.save()
        
        messages.success(request, "Comment posted successfully.")
    else:
        messages.error(request, "(403)Invalid method - please use form provided to post comments.", extra_tags="danger")
    return HttpResponseRedirect(reverse("listing", args=(id,)))

@login_required
def savewatcher(request, id):
    # Add or remove a listing from a user's watchlist
    item = Listing.objects.get(pk = id)
    if request.GET.get("remove", False):
        item.watchers.remove( request.user )
    else:
        item.watchers.add( request.user )
    
    # A somewhat hacky way of refreshing the page the user upadates their watchlist from
    # - I would look into neatening this up with a more formal method given more time
    # - currently when updating the users watchlist they send a url bool saying which page they're on
    
    if request.GET.get("froml", False): # from a listing (with id) page
        return HttpResponseRedirect(reverse("listing", args=(id,)))
    elif request.GET.get("fromw", False): # from the user's watchlist
        return HttpResponseRedirect(reverse("watchlist"))
    else: # active listings
        return HttpResponseRedirect(reverse("index"))

@login_required
def saveactive(request, id):
    # List or de-list an item
    item = Listing.objects.get(pk = id)
    item.active = not item.active
    item.save()
    
    return HttpResponseRedirect(reverse("listing", args=(id,)))


def allcategories(request):
    # Page that displays and links to all categories
    ctgry_links = Category.objects.all()
    return render(request, "auctions/allcategories.html", {
        "ctgry_links": ctgry_links,
        })

