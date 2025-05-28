import datetime
from django.utils import timezone

from app.models import Event, Venue, User
from app.test.test_e2e.base import BaseE2ETest  # Asumo que tienes esta clase base

class EventStatusE2ETest(BaseE2ETest):
    """E2E Tests para la funcionalidad de estado del evento"""

    def setUp(self):
        super().setUp()
        #  Crear un organizador y un evento de prueba (como en tu ejemplo)
        self.organizer = self.create_organizer()
        self.venue = self.create_venue(self.organizer)
        self.event = self.create_event(self.organizer, self.venue)

    def create_organizer(self):
        return User.objects.create_user(
            username="organizador",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )

    def create_venue(self, organizer):
        return Venue.objects.create(
            name="Test Venue",
            address="Test Address",
            city="Test City",
            capacity=100,
            contact_info="Test Info",
            created_by=organizer,
        )

    def create_event(self, organizer, venue, scheduled_at=None):
        if not scheduled_at:
            scheduled_at = timezone.now() + timezone.timedelta(days=1)
        return Event.objects.create(
            title="Test Event",
            description="Test Description",
            scheduled_at=scheduled_at,
            organizer=organizer,
            venue=venue,
        )

    def navigate_to_event_detail(self, event_id):
        self.page.goto(f"{self.live_server_url}/events/{event_id}/")

    def assert_event_status_is(self, expected_status):
        """Asegura que el estado del evento en la página coincide con el esperado."""
        status_element = self.page.locator("#event-status")  #  Selector para el elemento que muestra el estado
        self.assertTrue(status_element.is_visible())
        self.assertEqual(status_element.inner_text(), expected_status)


    def test_event_status_changes_on_event_detail(self):
        """
        Test E2E que verifica que el estado del evento se actualiza correctamente
        y se muestra en la página de detalle del evento.
        """

        #  1.  Iniciar sesión como organizador
        self.login_user("organizador", "password123")

        #  2.  Navegar a la página de detalle del evento
        self.navigate_to_event_detail(self.event.id)

        #  3.  Verificar el estado inicial (debería ser 'activo')
        self.assert_event_status_is("activo")

        #  4.  Modificar la fecha del evento para que sea en el pasado
        self.event.scheduled_at = timezone.now() - timezone.timedelta(days=1)
        self.event.save()

        #  5.  Recargar la página de detalle del evento
        self.page.reload()

        #  6.  Verificar que el estado se ha actualizado a 'finalizado'
        self.assert_event_status_is("finalizado")

        #  7.  (Opcional)  Simular la venta de todas las entradas y verificar 'agotado'
        self.event.tickets_sold = self.venue.capacity
        self.event.save()
        self.page.reload()
        self.assert_event_status_is("agotado")

        #  8.  (Opcional)  Verificar 'cancelado' (si tienes una forma de cambiarlo en la UI)
        #  ...