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
        # Inicia sesión con el usuario creado. Esto es crucial para simular
        # un usuario autenticado que interactúa con la aplicación.
        self.client.login(username="testuser", password="1234")

        # Ahora usamos los nombres de URL correctos basados en tu urls.py
        self.add_favorite_url = reverse("agregar_favorito", args=[self.event.id])
        self.remove_favorite_url = reverse("eliminar_favorito", args=[self.event.id])

    def test_add_and_remove_favorite_via_urls(self):
        """
        Verifica la funcionalidad de agregar y eliminar un evento de favoritos
        a través de las URLs específicas de agregar y eliminar.
        """
        # 1. Simular la adición de un evento a favoritos
        # Se envía una solicitud POST a la URL de agregar favorito.
        # follow=True es útil si tu vista redirige después de la acción.
        response_add = self.client.post(self.add_favorite_url, follow=True)

        # Verificar que la solicitud de adición fue exitosa (código 200 OK o 302 Redirect)
        # Tu vista 'agregar_favorito' redirige a 'HTTP_REFERER' o 'lista_favoritos'.
        # Si redirige, el status_code será 302. Si simplemente renderiza, será 200.
        # Dado que tu vista usa `redirect(request.META.get('HTTP_REFERER', 'lista_favoritos'))`,
        # el `follow=True` hará que el cliente siga la redirección, y el status_code final será 200.
        self.assertEqual(response_add.status_code, 200)

        # Verificar que el evento ahora está en la lista de favoritos del usuario
        self.assertTrue(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())
        self.assertEqual(Favorito.objects.filter(usuario=self.user).count(), 1)
        # Opcional: Verificar el mensaje de éxito si tu template lo muestra
        # self.assertContains(response_add, f"'{self.event.title}' añadido a favoritos")


        # 2. Simular la eliminación del evento de favoritos
        # Se envía una solicitud POST a la URL de eliminar favorito.
        response_remove = self.client.post(self.remove_favorite_url, follow=True)

        # Verificar que la solicitud de eliminación también fue exitosa
        self.assertEqual(response_remove.status_code, 200)

        # Verificar que el evento ya no está en la lista de favoritos del usuario
        self.assertFalse(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())
        self.assertEqual(Favorito.objects.filter(usuario=self.user).count(), 0)
        # Opcional: Verificar el mensaje de éxito si tu template lo muestra
        # self.assertContains(response_remove, f"'{self.event.title}' eliminado de favoritos")


    def test_add_favorite_requires_login(self):
        """
        Verifica que la funcionalidad de agregar favoritos requiere que el usuario esté autenticado.
        """
        self.client.logout() # Cierra la sesión del usuario para esta prueba

        # Intenta agregar un favorito sin estar logueado
        response = self.client.post(self.add_favorite_url, follow=True)

        # Tu configuración de Django (por defecto o en settings.py) redirige a la página de login
        # cuando se accede a una vista decorada con @login_required sin autenticación.
        # Asumiendo que tu LOGIN_URL es 'login' (que es el nombre de tu URL de login).
        self.assertRedirects(response, reverse("login") + "?next=" + self.add_favorite_url)

        # Verificar que el favorito no fue agregado porque el usuario no estaba autenticado
        self.assertFalse(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())
        self.assertEqual(Favorito.objects.filter(usuario=self.user).count(), 0)

    def test_remove_favorite_requires_login(self):
        """
        Verifica que la funcionalidad de eliminar favoritos requiere que el usuario esté autenticado.
        """
        # Primero, aseguramos que el evento esté en favoritos (lo haremos directamente en la DB para esta prueba)
        Favorito.objects.create(usuario=self.user, evento=self.event)
        self.assertTrue(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())

        self.client.logout() # Cierra la sesión del usuario para esta prueba

        # Intenta eliminar un favorito sin estar logueado
        response = self.client.post(self.remove_favorite_url, follow=True)

        # Debería redirigir a la página de login
        self.assertRedirects(response, reverse("login") + "?next=" + self.remove_favorite_url)

        # Verificar que el favorito NO fue eliminado porque el usuario no estaba autenticado
        self.assertTrue(Favorito.objects.filter(usuario=self.user, evento=self.event).exists())
        self.assertEqual(Favorito.objects.filter(usuario=self.user).count(), 1)