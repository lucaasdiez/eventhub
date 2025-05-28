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
        """Versión corregida para encontrar el estado en el HTML actual"""
        # Localizar la sección de estado usando el texto "Estado del Evento"
        status_header = self.page.get_by_text("Estado del Evento", exact=True)
    
        # Navegar al elemento hermano siguiente que contiene el badge
        status_element = status_header.locator("xpath=./following-sibling::span")
        
        # Esperar y verificar
        status_element.wait_for(state="visible", timeout=5000)
        actual_text = status_element.inner_text().strip()
        self.assertEqual(actual_text, expected_status)


    def test_event_status_changes_on_event_detail(self):
        # 1. Iniciar sesión
        self.login_user("organizador", "password123")
        
        # 2. Navegar a detalle de evento
        self.navigate_to_event_detail(self.event.id)
        
        # 3. Verificar estado inicial
        self.assert_event_status_is("Activo")
        
        # 4. Simular entradas agotadas (sin cambiar fecha)
        self.event.tickets_sold = self.venue.capacity
        self.event.save()
        self.page.reload()
        self.assert_event_status_is("Agotado")  # Primero probamos estado agotado
        
        # 5. Resetear tickets vendidos
        self.event.tickets_sold = 0
        self.event.save()
        
        # 6. Modificar fecha al pasado
        self.event.scheduled_at = timezone.now() - timezone.timedelta(days=1)
        self.event.save()
        self.page.reload()
        self.assert_event_status_is("Finalizado")  # Luego probamos estado finalizado