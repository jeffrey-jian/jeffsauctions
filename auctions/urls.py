from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<str:item>", views.listing, name="listing"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("close_listing/<str:item>", views.close_listing, name="close_listing"),
    path("categories", views.view_categories, name="view_categories"),
    path("watchlist", views.view_watchlist, name="view_watchlist"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("auctions_won", views.auctions_won, name="auctions_won"),
    path("edit_watchlist/<str:item>", views.edit_watchlist, name="edit_watchlist"),
    path("add_comment/<str:item>", views.add_comment, name="add_comment")
]
