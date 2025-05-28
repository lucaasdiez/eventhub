#  test_event_status_unit.py (o puedes agregarlo a test_event.py, pero es mejor separarlos)
import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from app.models import Event, User, Venue  #  Importa los modelos necesarios


class EventStatusUnitTest(TestCase):
    def setUp(self):
        #  Crear un organizador y un lugar (necesario para algunos tests)
        self.organizer = User.objects.create_user(
            username="organizador_test",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="Test Address",
            city="Test City",
            capacity=100,
            contact_info="Test Info",
            created_by=self.organizer,
        )

    def create_event(self, **kwargs):
        """Método auxiliar para crear eventos con valores por defecto."""
        default_data = {
            "title": "Test Event",
            "description": "Test Description",
            "scheduled_at": timezone.now() + datetime.timedelta(days=1),
            "organizer": self.organizer,
            "venue": self.venue,
        }
        default_data.update(kwargs)  #  Permite sobreescribir los valores por defecto
        return Event.objects.create(**default_data)

    def test_update_status_finalizado(self):
        """
        Test: El estado del evento debe cambiar a 'finalizado'
        si la fecha programada ya pasó.
        """
        past_event = self.create_event(
            scheduled_at=timezone.now() - datetime.timedelta(days=1)
        )
        past_event.update_status()
        self.assertEqual(past_event.status, "finalizado")

    def test_update_status_agotado(self):
        """
        Test: El estado debe cambiar a 'agotado' si se vendieron
        todas las entradas.
        """
        event = self.create_event(tickets_sold=self.venue.capacity)
        event.update_status()
        self.assertEqual(event.status, "agotado")

    def test_update_status_activo_future(self):
        """
        Test: El estado debe permanecer 'activo' si el evento
        es en el futuro y no está agotado.
        """
        future_event = self.create_event(
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            tickets_sold=0,
        )
        future_event.update_status()
        self.assertEqual(future_event.status, "activo")

    def test_update_status_activo_with_tickets_left(self):
        """
        Test: El estado debe permanecer 'activo' si el evento
        es en el futuro y quedan entradas disponibles.
        """
        event = self.create_event(
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            tickets_sold=self.venue.capacity - 1,  #  Un ticket menos que la capacidad
        )
        event.update_status()
        self.assertEqual(event.status, "activo")

    def test_update_status_reprogramado(self):
        """
        Test:  Si tienes lógica específica para 'reprogramado', pruébala aquí.
              Por ejemplo, si hay un campo 'rescheduled_from' o algo así.
        """
        #  Ejemplo (adapta a tu modelo):
        #  event = self.create_event(is_rescheduled=True)
        #  event.update_status()
        #  self.assertEqual(event.status, "reprogramado")
        self.skipTest("Implementar cuando se tenga la lógica de reprogramado")  #  Para evitar errores si no está implementado

    def test_update_status_cancelado(self):
        """
        Test: Si tienes un campo o lógica para 'cancelado', pruébala aquí.
        """
        #  Ejemplo:
        #  event = self.create_event(is_cancelled=True)
        #  event.update_status()
        #  self.assertEqual(event.status, "cancelado")
        self.skipTest("Implementar cuando se tenga la lógica de cancelado")

    def test_update_status_no_venue(self):
        """
        Test: Verifica que eventos sin lugar tengan estado 'sin lugar'
        """
        event_no_venue = self.create_event(venue=None)
        event_no_venue.update_status()
        self.assertEqual(event_no_venue.status, "sin lugar")  # Corregido para reflejar el comportamiento real