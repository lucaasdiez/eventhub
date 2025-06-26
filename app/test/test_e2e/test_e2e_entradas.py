from playwright.sync_api import expect
from django.test import LiveServerTestCase
from app.models import User

class LoginE2ETest(LiveServerTestCase):
    # Configurar Playwright en setUp y tearDown
    def setUp(self):
        super().setUp()
        from playwright.sync_api import sync_playwright

        # Crear usuario para login
        self.user = User.objects.create_user(
            username="usuario_test",
            password="contraseña_test"
        )

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()

    def tearDown(self):
        self.browser.close()
        self.playwright.stop()
        super().tearDown()

    def test_user_can_login_and_redirect(self):
        login_url = f"{self.live_server_url}/accounts/login/"
        home_url = f"{self.live_server_url}/"

        self.page.goto(login_url)

        self.page.fill('input[name="username"]', "usuario_test")
        self.page.fill('input[name="password"]', "contraseña_test")

        self.page.click('button[type="submit"]')

        self.page.wait_for_url(home_url, timeout=15000)

        assert self.page.url == home_url
