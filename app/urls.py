from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    
    path("events/", views.events, name="events"),
    path("events/create/", views.event_form, name="event_create"), 
    path("events/<int:pk>/", views.event_detail, name="event_detail"), 
    path("events/<int:pk>/edit/", views.event_form, name="event_edit"),  
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),
    path('venues/', views.venue_list, name='venue_list'),
    path('venues/create/', views.venue_form, name='venue_create'),
    path('venues/<int:id>/edit/', views.venue_form, name='venue_edit'),
    path('venues/<int:id>/delete/', views.venue_delete, name='venue_delete'),
]
    

