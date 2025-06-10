from datetime import datetime, timedelta

from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright, expect

from app.models import Event, User, Venue, Ticket


class NotificacionesCambioEventoE2ETest(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='e2euser', password='1234')
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="Calle Falsa",
            city="Ciudad",
            capacity=100,
            contact_info="info@test.com",
            created_by=self.user
        )
        self.event = Event.objects.create(
            title="Evento de Prueba",
            description="Descripción",
            scheduled_at=datetime.now() + timedelta(days=7),
            organizer=self.user,
            venue=self.venue
        )
        # Crear un ticket para el usuario
        Ticket.objects.create(
            user=self.user,
            event=self.event,
            type="GENERAL",  # o "VIP", según tus opciones válidas
            quantity=1
        )

    def test_notificacion_aparece_cuando_evento_cambia(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Login
            page.goto(f"{self.live_server_url}/accounts/login/")
            page.fill('input[name="username"]', 'e2euser')
            page.fill('input[name="password"]', '1234')
            page.click('button[type="submit"]')

            # Editar evento
            page.goto(f"{self.live_server_url}/events/{self.event.id}/edit/")
            page.fill('input[name="title"]', 'Evento de Prueba Editado')
            nueva_fecha = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M")
            page.fill('input[name="scheduled_at"]', nueva_fecha)
            page.click('button[type="submit"]')  # Asumiendo que el botón de guardar es un submit

            # Ir a notificaciones
            page.goto(f"{self.live_server_url}/notifications/")

            # Verificar que la notificación esté presente
            expect(page.locator("body")).to_contain_text("El evento ha tenido cambios:")

            browser.close()
