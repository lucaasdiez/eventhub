from datetime import datetime, timedelta

from django.test import LiveServerTestCase
from playwright.sync_api import sync_playwright

from app.models import Event, User, Venue


class TicketE2ETest(LiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='e2euser', password='1234')
        venue = Venue.objects.create(
            name="Test Venue", address="Calle Falsa", city="Ciudad", capacity=100,
            contact_info="info@test.com", created_by=self.user
        )
        self.event = Event.objects.create(
            title="Evento E2E",
            description="Descripción",
            scheduled_at=datetime.now() + timedelta(days=5),
            organizer=self.user,
            venue=venue
        )

    def test_resumen_actualiza_con_js(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Ir a login
            page.goto(f"{self.live_server_url}/accounts/login/")
            page.fill('input[name="username"]', 'e2euser')
            page.fill('input[name="password"]', '1234')
            page.click('button[type="submit"]')

            # Ir a página de compra
            page.goto(f"{self.live_server_url}/tickets/new/")

            # Seleccionar cantidad y tipo
            page.fill('#id_quantity', '4')
            page.select_option('#id_type', 'VIP')

            # Esperar que se actualice el resumen
            page.wait_for_timeout(500)  # medio segundo

            # Verificar el total
            total_text = page.inner_text('#total')
            assert total_text.strip() == '$440.00'

            browser.close()