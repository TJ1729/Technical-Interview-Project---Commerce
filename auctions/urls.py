from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("listing/<int:id>/postb", views.postbid, name="postbid"),
    path("listing/<int:id>/postc", views.postcomment, name="postcomment"),
    path("listing/<int:id>/savew", views.savewatcher, name="savewatcher"),
    path("listing/<int:id>/saveactive", views.saveactive, name="saveactive"),
    path("listing/new", views.listeditor, name="listeditor"),
    path("postl", views.postlisting, name="postlisting"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.allcategories, name="allcategories"),
]
