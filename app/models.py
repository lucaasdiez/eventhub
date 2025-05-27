from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet, Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone


class User(AbstractUser):
    is_organizer = models.BooleanField(default=False)

    @classmethod
    def validate_new_user(cls, email, username, password, password_confirm):
        errors = {}

        if email is None:
            errors["email"] = "El email es requerido"
        elif User.objects.filter(email=email).exists():
            errors["email"] = "Ya existe un usuario con este email"

        if username is None:
            errors["username"] = "El username es requerido"
        elif User.objects.filter(username=username).exists():
            errors["username"] = "Ya existe un usuario con este nombre de usuario"

        if password is None or password_confirm is None:
            errors["password"] = "Las contraseñas son requeridas"
        elif password != password_confirm:
            errors["password"] = "Las contraseñas no coinciden"

        return errors

class Venue(models.Model):
    name = models.CharField(max_length=200, blank=False)
    address = models.CharField(max_length=300, blank=False)
    city = models.CharField(max_length=100, blank=False)
    capacity = models.PositiveIntegerField(blank=False)
    contact_info = models.TextField(blank=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    @classmethod
    def validate(cls, name, address, city, capacity, contact_info):
        errors = {}

        if not name:
            errors["name"] = "El nombre es requerido"
        if not address:
            errors["address"] = "La dirección es requerida"
        if not city:
            errors["city"] = "La ciudad es requerida"
        if not capacity:
            errors["capacity"] = "La capacidad es requerida"
        elif int(capacity) <= 0:
            errors["capacity"] = "La capacidad debe ser mayor a cero"
        if not contact_info:
            errors["contact_info"] = "La información de contacto es requerida"

        return errors
    
    @classmethod
    def new(cls, name, address, city, capacity, contact_info, created_by):
        errors = Venue.validate( name, address, city, capacity, contact_info)

        if len(errors.keys()) > 0:
            return False, errors
        
        Venue.objects.create(
            name=name,
            address=address,
            city=city,
            capacity=capacity,
            contact_info=contact_info,
            created_by=created_by
        )
        return True, None
    
    
    def update(self, name, address, city, capacity, contact_info):
        self.name = name or self.name
        self.address = address or self.address
        self.city = city or self.city
        self.capacity = capacity or self.capacity
        self.contact_info = contact_info or self.contact_info
        self.save()


  
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    
class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_at = models.DateTimeField()  
    total_rating = models.IntegerField(default=0)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    categories = models.ManyToManyField(Category, blank=True)    
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    premium = models.BooleanField(default=False, verbose_name="Evento Premium")  
    available_tickets = models.PositiveIntegerField(default=0)
    tickets: QuerySet['Ticket']

    def __str__(self):
        return self.title

    @classmethod
    def validate(cls, title, description, scheduled_at):
        errors = {}

        if title == "":
            errors["title"] = "Por favor ingrese un titulo"

        if description == "":
            errors["description"] = "Por favor ingrese una descripcion"

        return errors

    @classmethod
    def new(cls, title, description, scheduled_at, organizer):
        errors = Event.validate(title, description, scheduled_at)

        if len(errors.keys()) > 0:
            return False, errors

        event= Event.objects.create(
            title=title,
            description=description,
            scheduled_at=scheduled_at,
            organizer=organizer,
        )
        if event.venue:
            event.update_availability()
        return event, None

    def update(self, title, description, scheduled_at, organizer):
        self.title = title or self.title
        self.description = description or self.description
        self.scheduled_at = scheduled_at or self.scheduled_at
        self.organizer = organizer or self.organizer
        self.save()
        
    def tickets_sold(self):
        """Total de entradas vendidas para este evento."""
        return self.tickets.aggregate(total=Sum('quantity'))['total'] or 0  
    
    def update_availability(self):
        """Actualiza available_tickets según el venue y tickets vendidos."""
        if self.venue:  # Si el evento tiene un venue asignado
            self.available_tickets = self.venue.capacity - self.tickets_sold()
            self.save(update_fields=['available_tickets'])




class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    title = models.CharField(max_length=120)
    content =models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.title.strip():
            raise ValidationError("El titulo del comentario no puede estar vacio....")
        if not self.content.strip():
            raise ValidationError("El contenido del comentario no debe de estar vacio para realizar el comentario...")
        
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"



class Ticket(models.Model):
    GENERAL = 'GENERAL'
    VIP = 'VIP'
    TYPE_CHOICES = [
        (GENERAL, 'General'),
        (VIP, 'VIP'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    buy_date = models.DateField(auto_now_add=True)
    ticket_code = models.CharField(max_length=50, unique=True, editable=False)
    quantity = models.PositiveIntegerField(default=1)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=GENERAL)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2) 
    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            prefix = 'VIP' if self.type == self.VIP else 'GEN'
            super().save(*args, **kwargs)
            self.ticket_code = f"{prefix}-{self.pk:04d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_code} - {self.type}"



class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '🕒 Pendiente'),
        ('approved', '✅ Aprobado'),
        ('rejected', '❌ Rechazado'),
        ('refunded', '💰 Reembolsado')
    ]
    id = models.AutoField(primary_key=True, verbose_name="ID")
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="refunds")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField("Motivo del reembolso")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    percentage = models.IntegerField(default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    policy_30_days = models.BooleanField( default=False, verbose_name="Extensión de 30 días (Premium)")

    def __str__(self):
        return f"Reembolso #{self.id}"  

    def calcular_monto(self):
        """Calcula el monto según políticas"""
        tiempo_restante = self.ticket.event.scheduled_at - timezone.now()

        # Lógica de porcentaje
        if self.ticket.event.premium and tiempo_restante > timedelta(days=30):
            self.percentage = 100
        elif tiempo_restante > timedelta(days=7):
            self.percentage = 100
        elif tiempo_restante >= timedelta(days=2):
            self.percentage = 50
        else:
            self.percentage = 0

        # Cálculo del monto y guardado
        self.amount = self.ticket.price_paid * (Decimal(self.percentage) / Decimal(100))
        self.save()

    def is_refund_allowed(self):
        """Valida si el reembolso es permitido"""
        tiempo_restante = self.ticket.event.scheduled_at - timezone.now()
        
        if self.ticket.used:
            return False, "Ticket ya utilizado"
            
        if tiempo_restante < timedelta(hours=48):
            return False, "Menos de 48 horas para el evento"
            
        if self.ticket.event.premium and (timezone.now() - self.ticket.event.scheduled_at) > timedelta(days=30):
            return False, "Pasaron 30 días del evento (premium)"
            
        return True, "Reembolso permitido"

@receiver([post_save, post_delete], sender=Ticket)
def update_event_availability(sender, instance, **kwargs):
    """Actualiza disponibilidad al crear/eliminar tickets."""
    instance.event.update_availability()