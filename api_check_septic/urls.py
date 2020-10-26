from django.contrib import admin
from django.urls import path
from .views import check_septic

urlpatterns = [
    # all the interesting stuff is left to the root app's urlconf
    path("", check_septic, name="check_septic"),
]