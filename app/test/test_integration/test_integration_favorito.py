from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from app.models import Event, Favorito

User = get_user_model()

class FavoritoIntegrationTest(TestCase):
    """
    Clase para pruebas de integración de la funcionalidad de favoritos.
    Simula la interacción de un usuario a través de solicitudes HTTP.
    """

    def setUp(self):
        """
        Configuración inicial para cada prueba.
        Crea un usuario, un evento y un cliente para simular solicitudes.
        """
        self.client = Client()  # Crea un cliente para hacer solicitudes HTTP
        self.user = User.objects.create_user(username="testuser", password="1234")
        self.event = Event.objects.create(
            title="Test Event",
            description="Evento de prueba para favoritos",
            scheduled_at=timezone.now() + timezone.timedelta(days=5),
            organizer=self.user
        )
        
        self.client.login(username="testuser", password="1234")

        
        self.add_favorite_url = reverse("agregar_favorito", args=[self.event.id])
        self.remove_favorite_url = reverse("eliminar_favorito", args=[self.event.id])

    def test_add_and_remove_favorite_via_urls(self):
        """
        Verifica la funcionalidad de agregar y eliminar un evento de favoritos
        a través de las URLs específicas de agregar y eliminar.
        """
       
        response_add = self.client.post(self.add_favorite_url, follow=True)
        self.assertEqual(response_add.status_code, 200)
        self.assertTrue(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())
        self.assertEqual(Favorito.objects.filter(usuario=self.user).count(), 1)
       
        response_remove = self.client.post(self.remove_favorite_url, follow=True)
       
        self.assertEqual(response_remove.status_code, 200)
        self.assertFalse(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())
        self.assertEqual(Favorito.objects.filter(usuario=self.user).count(), 0)
       
    def test_add_favorite_requires_login(self):
        """
        Verifica que la funcionalidad de agregar favoritos requiere que el usuario esté autenticado.
        """
        self.client.logout()         
        response = self.client.post(self.add_favorite_url, follow=True)
       
        self.assertRedirects(response, reverse("login") + "?next=" + self.add_favorite_url)     
        self.assertFalse(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())
        self.assertEqual(Favorito.objects.filter(usuario=self.user).count(), 0)

    def test_remove_favorite_requires_login(self):
        """
        Verifica que la funcionalidad de eliminar favoritos requiere que el usuario esté autenticado.
        """
        Favorito.objects.create(usuario=self.user, evento=self.event)
        self.assertTrue(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())

        self.client.logout()        
        response = self.client.post(self.remove_favorite_url, follow=True)       
        self.assertRedirects(response, reverse("login") + "?next=" + self.remove_favorite_url)       
        self.assertTrue(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())
        self.assertEqual(Favorito.objects.filter(usuario=self.user).count(), 1)