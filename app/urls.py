from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    path("events/", views.events, name="events"),
    path("events/create/", views.event_form, name="event_form"),
    path("events/<int:id>/edit/", views.event_form, name="event_edit"),
    path("events/<int:id>/", views.event_detail, name="event_detail"),
    path("events/<int:id>/delete/", views.event_delete, name="event_delete"),

    path('tickets/<int:ticket_id>/refund/', 
         views.request_refund, 
         name='request_refund'),

    # Gestión de reembolsos (organizador)
    path('refunds/', 
         views.manage_refunds, 
         name='manage_refunds'),

    # Detalle de reembolso (ambos roles)
    path('refunds/<int:refund_id>/', 
         views.refund_detail, 
         name='refund_detail'),

    # Acción unificada de aprobar/rechazar (organizador)
    path('refunds/<int:refund_id>/<str:action>/',  # <- Cambio clave aquí
         views.update_refund_status, 
         name='update_refund_status'),
]
