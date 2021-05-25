from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from datetime import datetime

from .models import User, Listings, Bids, Watchlist, Category, Comments


# create new listing form
class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['title', 'description', 'image_url', 'category']
        labels = {
            'image_url': 'Image URL'
        }

class StartingBidForm(forms.ModelForm):
    class Meta:
        model = Bids
        fields = ['price']
        labels = {
            'price': 'Starting Bid'
        }


def index(request):
    user = request.user
    print(user)
    print('....................................................................')
    my_watchlist = []
    listings = Listings.objects.all().order_by('created_date').reverse()
    if request.user.is_authenticated:
        #my_watchlist contains ID of listings
        my_watchlist = Watchlist.objects.filter(user=user).values_list('listing', flat=True)
        print(my_watchlist)
        print(".........................................................................")
    else:
        print("not logged in .............................................................")
    return render(request, "auctions/index.html", {
        "listings": listings,
        "my_watchlist": my_watchlist,
    })

def listing(request, item):
    watchlisted = []
    creator = False
    logged_in = request.user.is_authenticated
    listing = Listings.objects.get(title=item)
    bids_count = Bids.objects.filter(listing=listing).count()
    highest_bid = Bids.objects.filter(listing=listing).order_by('price').reverse().first()
    comments = Comments.objects.filter(listing=listing).order_by('created_date').reverse()
    if logged_in:
        user = request.user
        watchlisted = Watchlist.objects.filter(user=user,listing=listing)
        if user == listing.created_user:
            creator = True
    
    # minimum bid amount
    if listing.highest_bid:
        minimum_bid = listing.highest_bid
    else:
        minimum_bid = listing.starting_bid

    if request.method == "POST":
        bid_quote = request.POST.get("bid_quote")
        
        # if invalid bid amount
        print(bid_quote)
        print(minimum_bid)
        if float(bid_quote) <= float(minimum_bid):
            message = "You must bid above the current price!"
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "bids_count": bids_count,
                "minimum_bid": minimum_bid,
                "highest_bid": highest_bid,
                "message": message,
                "watchlisted": watchlisted,
                "logged_in": logged_in,
                "comments": comments,
                "creator": creator,
                
            })
        
        # key bid into Bids
        new_bid = Bids(
            listing=listing,
            price=bid_quote,
            user=user
        )
        new_bid.save()
        # update highest bid
        Listings.objects.filter(title=item).update(highest_bid=bid_quote)
        # update watchlist
        if watchlisted.exists():
            Watchlist.objects.filter(user=user,listing=listing).update(last_update=datetime.now())
        else:
            new_watchlist = Watchlist(
                user=user,
                listing=listing
            )
            new_watchlist.save()

        return HttpResponseRedirect(reverse("view_watchlist"))
        
    # check if current logged in user has the highest bid
    if highest_bid and logged_in == True: 
        if highest_bid.user == user:
            highest_bid = True
    
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids_count": bids_count,
        "minimum_bid": minimum_bid,
        "highest_bid": highest_bid,
        "watchlisted": watchlisted,
        "logged_in": logged_in,
        "comments": comments,
        "creator": creator
    })




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
        return render(request, "auctions/login.html")


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
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        listing_form = NewListingForm(request.POST)
        bid_form = StartingBidForm(request.POST)
        if listing_form.is_valid() and bid_form.is_valid():
            title = listing_form.cleaned_data["title"]
            description = listing_form.cleaned_data["description"]
            image_url = listing_form.cleaned_data["image_url"]
            category = listing_form.cleaned_data["category"]
            price = bid_form.cleaned_data["price"]
            user = request.user

            # check if listing with same title exists
            if Listings.objects.filter(title=title).exists():
                message = "A listing with the same title exists! Please use another title."
                return render(request, "auctions/create_listing.html", {
                    "listing_form": NewListingForm,
                    "bid_form": StartingBidForm,
                    "message": message
                })
            else:
                # add new listing into database
                new_listing = Listings(
                    title=title,
                    description=description,
                    image_url=image_url,
                    category=category,
                    created_user=user,
                    starting_bid=price
                )
                new_listing.save()

                messages.info(request, 'Success! Your listing has been created')
                return HttpResponseRedirect(reverse('index'))

    return render(request, "auctions/create_listing.html", {
        "listing_form": NewListingForm,
        "bid_form": StartingBidForm
    })

@login_required
def close_listing(request, item):
    if request.method == "POST":
        listing = Listings.objects.get(title=item)
        if Bids.objects.filter(listing=listing).exists():
            highest_bid = Bids.objects.filter(listing=listing).order_by('price').reverse().first()
            winner = highest_bid.user
            listing.winner = winner
        listing.active = False
        listing.save()

        
    return HttpResponseRedirect(reverse('index'))



@login_required
def view_categories(request):
    categories = Category.objects.all()
    if request.method == "POST":
        my_watchlist = []
        category_chosen = request.POST.get("category_chosen")
        category_id = Category.objects.get(category=category_chosen)
        listings_chosen = Listings.objects.filter(category=category_id, active=True).order_by('created_date').reverse()
        if request.user.is_authenticated:
                user = request.user
                #my_watchlist contains ID of listings
                my_watchlist = Watchlist.objects.filter(user=user).values_list('listing', flat=True)

        return render(request,"auctions/view_categories.html", {
            "categories": categories,
            "listings_chosen": listings_chosen,
            "category_chosen": category_chosen,
            "my_watchlist": my_watchlist
        })

    return render(request, "auctions/view_categories.html", {
        "categories": categories,
    })

@login_required
def view_watchlist(request):
    user = request.user
    listings = Listings.objects.all().order_by('created_date').reverse()
    #my_watchlist contains ID of listings
    my_watchlist = Watchlist.objects.filter(user=user).values_list('listing', flat=True)
    return render(request, "auctions/view_watchlist.html", {
        "listings": listings,
        "my_watchlist": my_watchlist,
    })

@login_required
def auctions_won(request):
    user = request.user
    listings = Listings.objects.filter(winner=user)
    #my_watchlist contains ID of listings
    my_watchlist = Watchlist.objects.filter(user=user).values_list('listing', flat=True)
    return render(request, "auctions/auctions_won.html", {
        "listings": listings,
        "my_watchlist": my_watchlist
    })

@login_required
def my_listings(request):
    user = request.user
    listings = Listings.objects.filter(created_user=user)
    #my_watchlist contains ID of listings
    my_watchlist = Watchlist.objects.filter(user=user).values_list('listing', flat=True)
    return render(request, "auctions/my_listings.html", {
        "listings": listings,
        "my_watchlist": my_watchlist
    })


@login_required
def edit_watchlist(request, item):
    user = request.user
    listing = Listings.objects.get(title=item)
    watchlisted = Watchlist.objects.filter(user=user,listing=listing)
    if watchlisted.exists():
        watchlisted.delete()
    else:
        new_watchlist = Watchlist(
            user=user,
            listing=listing
        )
        new_watchlist.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def add_comment(request, item):
    if request.method == "POST":
        user = request.user
        listing = Listings.objects.get(title=item)
        comment = request.POST.get("comment")
        new_comment = Comments(
            listing=listing,
            comment=comment,
            created_user=user,
        )
        new_comment.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
