import datetime
from django.utils import timezone
from app.models import Event, Venue, User
from app.test.test_e2e.base import BaseE2ETest
from playwright.sync_api import expect

class EventStatusE2ETest(BaseE2ETest):

    def setUp(self):
        super().setUp()
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
            scheduled_at = timezone.now() + timezone.timedelta(days=7) 
        return Event.objects.create(
            title="Test Event",
            description="Test Description",
            scheduled_at=scheduled_at,
            organizer=organizer,
            venue=venue,
            available_tickets=venue.capacity
        )

    def navigate_to_event_detail(self, event_id):
        self.page.goto(f"{self.live_server_url}/events/{event_id}/")
        expect(self.page.locator("h1:has-text('Test Event')")).to_be_visible(timeout=10000)

    def assert_event_status_is(self, expected_status):
        status_locator = self.page.locator("[data-test='event-status']")
        expect(status_locator).to_be_visible(timeout=10000)
        expect(status_locator).to_have_text(expected_status)

    def test_event_status_changes(self):
        self.login_user("organizador", "password123")

        self.navigate_to_event_detail(self.event.id)
        self.assert_event_status_is("Activo")
        
        self.event.tickets_sold = self.event.available_tickets
        self.event.save()
        self.page.reload(wait_until="networkidle")
        self.assert_event_status_is("Agotado")
        
        self.event.scheduled_at = timezone.now() - datetime.timedelta(days=1)
        self.event.save()
        self.page.reload(wait_until="networkidle")
        self.assert_event_status_is("Finalizado")
