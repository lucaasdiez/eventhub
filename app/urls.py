from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views
from .views import TicketCreateView, TicketDeleteView, TicketListView, TicketUpdateView

urlpatterns = [

    path("", views.home, name="home"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    
    path("events/", views.events, name="events"),
    path("events/create/", views.event_form, name="event_create"), 
    path("events/<int:id>/", views.event_detail, name="event_detail"), 
    path("events/<int:id>/edit/", views.event_form, name="event_edit"),  
    path("events/<int:id>/delete/", views.event_delete, name="event_delete"),
    path("events/<int:event_id>/buy/", TicketCreateView.as_view(), name="ticket_create"),

    path('venues/', views.venue_list, name='venue_list'),
    path('venues/create/', views.venue_form, name='venue_create'),
    path('venues/<int:id>/edit/', views.venue_form, name='venue_edit'),
    path('venues/<int:id>/delete/', views.venue_delete, name='venue_delete'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    path('comment/', views.comentarios_organizador, name='comentarios_organizador'),
    path('comentarios/eliminar/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),

    path('tickets/', TicketListView.as_view(), name='ticket_list'),
    path('tickets/new/', TicketCreateView.as_view(), name='ticket_form'),
    path('tickets/<int:pk>/edit/', TicketUpdateView.as_view(), name='ticket_update'),
    path('tickets/<int:pk>/delete/', TicketDeleteView.as_view(), name='ticket_delete'),

    path('refunds/request/', views.request_refund, name='request_refund'),
    path('refunds/', views.manage_refunds, name='manage_refunds'),
    path('refunds/<int:refund_id>/', views.refund_detail, name='refund_detail'),
    path('refunds/<int:refund_id>/<str:action>/', views.update_refund_status, name='update_refund_status'),
]
    

