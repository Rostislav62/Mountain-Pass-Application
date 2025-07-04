import random
from django.core.mail import send_mail
from django.conf import settings
from main.models import EmailConfirmationToken

def generate_confirmation_code():
    """Генерирует 6-значный код подтверждения"""
    return str(random.randint(100000, 999999))

def send_confirmation_email(user):
    """Отправляет код подтверждения на email пользователя"""
    code = generate_confirmation_code()

    # Сохраняем код в базе (если код уже есть, обновляем его)
    token, created = EmailConfirmationToken.objects.update_or_create(
        user=user, defaults={'code': code}
    )

    subject = "Подтверждение изменения данных"
    message = f"Ваш код подтверждения для изменения данных: {code}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
