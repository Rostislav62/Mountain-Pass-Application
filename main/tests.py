from django.test import TestCase
from rest_framework.test import APIClient
from main.models import User


class RegisterTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        """Тестируем регистрацию нового пользователя"""
        response = self.client.post('/api/auth/register/', {
            "email": "test@example.com",
            "fam": "Иванов",
            "name": "Иван",
            "otc": "Иванович",
            "phone": "+79001112233"
        })

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())
