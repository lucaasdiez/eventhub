from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

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

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_at = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Campo nuevo requerido
    premium = models.BooleanField(default=False, verbose_name="Evento Premium")  

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

        return Event.objects.create(
            title=title,
            description=description,
            scheduled_at=scheduled_at,
            organizer=organizer,
        ), None

    def update(self, title, description, scheduled_at, organizer):
        self.title = title or self.title
        self.description = description or self.description
        self.scheduled_at = scheduled_at or self.scheduled_at
        self.organizer = organizer or self.organizer
        self.save()

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tickets")
    code = models.CharField(max_length=20, unique=True)
    used = models.BooleanField(default=False)
    purchase_date = models.DateTimeField(auto_now_add=True)
    # Campo requerido para los cálculos
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)  

    def __str__(self):
        return f"Ticket {self.code}"

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
    policy_30_days = models.BooleanField(
        default=False,
        verbose_name="Extensión de 30 días (Premium)"
    )

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