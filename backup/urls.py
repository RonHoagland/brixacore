from django.urls import path
from . import views

urlpatterns = [
    path("", views.backup_dashboard_view, name="backup_dashboard"),
    path("trigger/", views.trigger_backup_view, name="trigger_backup"),
]
