from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
   
    def __str__(self):
        return f"{self.username}[ID:{self.id}]"
    

# listing categories 
class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"
    
    

# auction listings 
class Listings(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=300, blank=True)
    category = models.ForeignKey(Category, related_name="similar_listings", on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(User, related_name="my_listings", on_delete=models.PROTECT)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    highest_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, related_name="listings_won", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"[{self.title}] under [{self.category}] category created by [{self.created_user}] on [{self.created_date}]"

# bids
class Bids(models.Model):
    listing = models.ForeignKey(Listings, related_name="bids", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, related_name="my_biddings", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"[{self.user}] bid [${self.price}] on [{(self.listing).title}]"


# comments on listings
class Comments(models.Model):
    listing = models.ForeignKey(Listings, related_name="comments", on_delete=models.CASCADE)
    comment = models.TextField()
    created_user = models.ForeignKey(User, related_name="my_comments", on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_user} commented on {self.listing.title} on {self.created_date}: {self.comment}"

# watchlist
class Watchlist(models.Model):
    user = models.ForeignKey(User, related_name="watchlist", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listings, related_name="watchlisted_users", on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} watchlisted {self.listing.title} at {self.last_update}"