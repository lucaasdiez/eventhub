from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("", views.home, name="home"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    
    # Events
    path("events/", views.events, name="events"),
    path("events/create/", views.event_form, name="event_create"), 
    path("events/<int:pk>/", views.event_detail, name="event_detail"), 
    path("events/<int:pk>/edit/", views.event_form, name="event_edit"),  
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),
]