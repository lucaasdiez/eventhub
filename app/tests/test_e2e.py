from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.models import User

class EventHubE2ETest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        service = Service('C:/ruta/a/chromedriver.exe')  # Ajustar ruta chromedriver
        cls.browser = webdriver.Chrome(service=service)
        cls.browser.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username="usuario_test", password="contraseña_test")

    def test_login_redirects_to_events(self):
        self.browser.get(f'{self.live_server_url}/accounts/login/')
        self.browser.find_element(By.NAME, 'username').send_keys('usuario_test')
        self.browser.find_element(By.NAME, 'password').send_keys('contraseña_test')
        self.browser.find_element(By.CSS_SELECTOR, 'button[type=submit]').click()

        WebDriverWait(self.browser, 10).until(
            EC.url_contains('/events/')
        )
        self.assertIn('/events/', self.browser.current_url)