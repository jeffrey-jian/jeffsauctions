from django.contrib import admin
from .models import User, Category, Listings, Bids, Watchlist, Comments

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Listings)
admin.site.register(Bids)
admin.site.register(Watchlist)
admin.site.register(Comments)