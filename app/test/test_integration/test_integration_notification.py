from django.test import TestCase
from django.urls import reverse
from app.models import User, Event, Ticket, Venue, Notification
from datetime import timedelta
from django.utils import timezone


class NotificacionCambioEventoIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="integrationuser", password="1234")
        self.client.login(username="integrationuser", password="1234")
        
        self.venue = Venue.objects.create(
            name="Venue Test",
            address="Calle Falsa 123",
            city="Ciudad",
            capacity=100,
            contact_info="contacto@ejemplo.com",
            created_by=self.user
        )

        self.event = Event.objects.create(
            title="Evento Integración",
            description="Test de notificación",
            scheduled_at=timezone.now() + timedelta(days=7),
            organizer=self.user,
            venue=self.venue,
            available_tickets=10
        )

        # Compra un ticket
        Ticket.objects.create(user=self.user, event=self.event, type="GENERAL", quantity=1, price_paid=100)

    def test_crea_notificacion_al_cambiar_fecha(self):
        # Simula un cambio en la fecha del evento
        nueva_fecha = self.event.scheduled_at + timedelta(days=3)

        response = self.client.post(reverse('event_edit', kwargs={'id': self.event.id}), {
            'title': self.event.title,
            'description': self.event.description,
            'scheduled_at': nueva_fecha.strftime('%Y-%m-%dT%H:%M'),
            'venue': self.venue.id,
        })

        self.assertEqual(response.status_code, 302)

        notificaciones = Notification.objects.filter(user=self.user)
        self.assertEqual(notificaciones.count(), 1)
        self.assertIn("El evento ha tenido cambios:", notificaciones.first().text)

    def test_crea_notificacion_al_cambiar_lugar(self):
        # Crear un nuevo venue
        nuevo_venue = Venue.objects.create(
            name="Nuevo Lugar",
            address="Otra calle 999",
            city="Otra ciudad",
            capacity=200,
            contact_info="nuevo@ejemplo.com",
            created_by=self.user
        )

        response = self.client.post(reverse('event_edit', kwargs={'id': self.event.id}), {
            'title': self.event.title,
            'description': self.event.description,
            'scheduled_at': self.event.scheduled_at.strftime('%Y-%m-%dT%H:%M'),
            'venue': nuevo_venue.id,
        })

        self.assertEqual(response.status_code, 302)

        notificaciones = Notification.objects.filter(user=self.user)
        self.assertEqual(notificaciones.count(), 1)
        self.assertIn("El evento ha tenido cambios:", notificaciones.first().text)
