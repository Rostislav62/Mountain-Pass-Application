#  /Mountain Pass Application/config/urls.py

from django.http import JsonResponse
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


# Функция заглушка для главной страницы
def index(request):
    return JsonResponse({"message": "API работает! Используйте /api/ для доступа к методам."})


urlpatterns = [
    path('', index),  # Теперь корневой URL отвечает JSON-сообщением
    path('admin/', admin.site.urls),
    path('api/', include('main.urls')),  # Подключаем API
]

# Добавляем маршруты для обработки медиа-файлов **только в режиме DEBUG**
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)