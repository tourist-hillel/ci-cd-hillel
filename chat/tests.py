from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from channels.testing import WebsocketCommunicator
from chatapp.asgi import application
import json

class ChatTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

        data = {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse('chat'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    async def test_websocket_auth(self):
        communicator = WebsocketCommunicator(application, '/ws/chat/')
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

        communicator = WebsocketCommunicator(application, '/ws/chat/')
        communicator.scope['user'] = self.user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({'message': 'Test message'})
        response = await communicator.receive_json_from()
        self.assertEqual(response['username'], 'testuser')
        self.assertEqual(response['message'], 'Test message')

        await communicator.disconnect()