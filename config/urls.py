#  /Mountain Pass Application/config/urls.py

from django.http import JsonResponse
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import get_resolver
from rest_framework.authentication import SessionAuthentication


# Функция заглушка для главной страницы
def index(request):
    return JsonResponse({"message": "API работает! Используйте /api/ для доступа к методам."})


urlpatterns = [
    path('', index),  # Теперь корневой URL отвечает JSON-сообщением
    path('admin/', admin.site.urls),
    path('api/', include('main.urls')),  # Подключаем API
]

# Добавляем маршруты для обработки медиа-файлов **только в режиме DEBUG**
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#     schema_view = get_schema_view(
#         openapi.Info(
#             title="Mountain Pass API",
#             default_version="v1",
#             description="Документация API для проекта Mountain Pass Application",
#         ),
#         public=True,
#         permission_classes=[permissions.AllowAny],
#     )
#
#     urlpatterns = [
#         re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#         re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
#     ]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


schema_view = get_schema_view(
    openapi.Info(
        title="Mountain Pass API",
        default_version="v1",
        description="Документация API для проекта Mountain Pass Application",
    ),
    public=True,
    authentication_classes=[],  # Полностью убираем любую аутентификацию
    permission_classes=[permissions.AllowAny],  # Swagger должен быть доступен всем
)

# Отключаем редирект на логин
urlpatterns += [
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger.json$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]



def list_urls(request):
    """Выводит все маршруты Django в JSON-формате."""
    urls = [str(url.pattern) for url in get_resolver().url_patterns]
    return JsonResponse({"routes": urls})


urlpatterns += [
    path('debug/urls/', list_urls),  # Временный эндпоинт для просмотра маршрутов
]
