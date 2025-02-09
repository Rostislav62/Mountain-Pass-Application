#  /Mountain Pass Application/config/urls.py

from django.http import JsonResponse
from django.urls import path, include
from django.contrib import admin


# Функция заглушка для главной страницы
def index(request):
    return JsonResponse({"message": "API работает! Используйте /api/ для доступа к методам."})


urlpatterns = [
    path('', index),  # Теперь корневой URL отвечает JSON-сообщением
    path('admin/', admin.site.urls),
    path('api/', include('main.urls')),  # Подключаем API
]

