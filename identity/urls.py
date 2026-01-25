from django.urls import path
from . import views

urlpatterns = [
    path("users/", views.user_list_view, name="user_list"),
    path("users/<int:pk>/", views.user_detail_view, name="user_detail"),
]
