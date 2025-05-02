# app/admin.py
from django.contrib import admin

from .models import Event, RefundRequest, Ticket

admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(RefundRequest)