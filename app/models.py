from django.contrib.auth.models import AbstractUser
from django.db import models


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
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_at = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

        Event.objects.create(
            title=title,
            description=description,
            scheduled_at=scheduled_at,
            organizer=organizer,
        )

        return True, None

    def update(self, title, description, scheduled_at, organizer):
        self.title = title or self.title
        self.description = description or self.description
        self.scheduled_at = scheduled_at or self.scheduled_at
        self.organizer = organizer or self.organizer

        self.save()

class Ticket(models.Model):
    GENERAL = 'GENERAL'
    VIP = 'VIP'
    TYPE_CHOICES = [
        (GENERAL, 'General'),
        (VIP, 'VIP'),
    ]

    # Relación con User
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE, #Si borro el User también se van a borrar los tickets asociados
        related_name='tickets' #Permite el uso de user.tickets.all() para obtener todos los tickets de un usuario
    )
    
    # Relación con Event
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE, #Si borro el evento, se van a borrar los tickets asociados
        related_name='tickets'
    )
    
    #Atributos de Ticket
    buy_date = models.DateField(auto_now_add=True)
    ticket_code = models.CharField(max_length=50, unique=True, editable=False)
    quantity = models.PositiveIntegerField(default=1)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=GENERAL)

    def save(self, *args, **kwargs):
        if not self.ticket_code:
            prefix = 'VIP' if self.type == self.VIP else 'GEN'
            super().save(*args, **kwargs)
            self.ticket_code = f"{prefix}-{self.pk:04d}"
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_code} - {self.type}"