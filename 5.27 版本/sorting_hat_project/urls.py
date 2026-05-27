"""URL configuration for sorting_hat_project project."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sorting_hat.urls')),
]