from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.messages import get_messages
from app.models import User, Event, Favorito

class AddToFavoritesE2ETest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123',
            is_organizer=True
        )
        self.event = Event.objects.create(
            title='Fiesta de la Cerveza',
            description='Evento sobre cerveza',
            scheduled_at=timezone.now() + timezone.timedelta(days=5),
            organizer=self.user
        )
        self.client.login(username='testuser', password='testpass123')

    def test_user_can_add_event_to_favorites(self):
        url = reverse('agregar_favorito', args=[self.event.id])
        
        response = self.client.post(url, follow=True)
        
        # Verificaciones básicas
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Favorito.objects.filter(usuario=self.user, evento=self.event).exists(),
            "El favorito no se creó en la base de datos"
        )
        
        # Verifica que se redirigió a la lista de favoritos
        self.assertTemplateUsed(response, 'app/event/favoritos/lista.html')
        
        # Opcional: Verifica que el evento aparece en la lista
        self.assertContains(response, self.event.title)

    def test_add_favorite_redirects_properly(self):
        url = reverse('agregar_favorito', args=[self.event.id])
        response = self.client.post(url)  # Sin follow
        
        self.assertEqual(response.status_code, 302)
        
        # Opción 1: Para Django >= 3.0 (más moderno)
        self.assertEqual(response.headers['Location'], reverse('lista_favoritos'))
        
        # Opción 2: Alternativa compatible con versiones anteriores
        self.assertIn(reverse('lista_favoritos'), response.get('Location', ''))

    def test_user_can_remove_from_favorites(self):
        # Primero agregamos un favorito
        Favorito.objects.create(usuario=self.user, evento=self.event)
        
        url = reverse('eliminar_favorito', args=[self.event.id])
        response = self.client.post(url, follow=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Favorito.objects.filter(usuario=self.user, evento=self.event).exists(),
            "El favorito no se eliminó correctamente"
        )
        # Verifica que se redirigió a la lista vacía
        self.assertContains(response, "Aún no tienes eventos favoritos")

    def test_anonymous_cannot_add_favorites(self):
        self.client.logout()
        url = reverse('agregar_favorito', args=[self.event.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 302)  # Redirige a login
        self.assertFalse(Favorito.objects.exists())

    # Test adicional para verificar mensajes (si usas Django messages)
    def test_add_favorite_shows_message(self):
        url = reverse('agregar_favorito', args=[self.event.id])
        response = self.client.post(url, follow=True)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('añadido a favoritos', str(messages[0]))