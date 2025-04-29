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
    title = models.CharField(max_length=200, blank=False) #blank = false, atributo requerido en la creacion
    description = models.TextField(blank=False)
    scheduled_at = models.DateTimeField(blank=False)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events", blank=False)
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




