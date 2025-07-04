# /Mountain Pass Application/config/urls.py

from django.http import JsonResponse  # Для ответа JSON-данными
from django.urls import path, include, re_path  # Для настройки маршрутов
from django.contrib import admin  # Django админ-панель
from django.conf import settings  # Подключаем настройки проекта
from django.conf.urls.static import static  # Для работы со статическими и медиа-файлами
from rest_framework import permissions  # Разрешения для Swagger
from drf_yasg.views import get_schema_view  # Генератор документации Swagger
from drf_yasg import openapi  # Конфигурация OpenAPI
from django.contrib.auth.models import User  # Django модель пользователя
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # JWT-токены
from main.views import RegisterView, UserDetailView, RequestUserUpdateView, \
    ConfirmUserUpdateView, UserSubmitsView  # API для регистрации пользователей
from django.urls import get_resolver  # Для получения списка маршрутов


# 📌 Функция заглушка для главной страницы API
def index(request):
    return JsonResponse({"message": "API работает! Используйте /api/ для доступа к методам."})


# 📌 Настройка Swagger UI и Redoc документации
schema_view = get_schema_view(
    openapi.Info(
        title="Mountain Pass API",
        default_version="v1",
        description="Документация API для проекта Mountain Pass Application",
    ),
    public=True,  # Swagger будет доступен всем пользователям
    authentication_classes=[],  # Полностью отключаем аутентификацию для Swagger
    permission_classes=[permissions.AllowAny],  # Swagger доступен без авторизации
)


# 📌 Основные маршруты API
urlpatterns = [
    # Главная страница API
    path('', index),

    # Django админ-панель
    path('admin/', admin.site.urls),

    # Основные API маршруты (подключаем маршруты из приложения `main`)
    path('api/', include('main.urls')),

    # JWT-аутентификация
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Получение токена
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Обновление токена
    path('api/auth/register/', RegisterView.as_view(), name='register'),  # Регистрация нового пользователя

    # Запросить код подтверждения
    path('api/auth/users/<str:email>/request-update/', RequestUserUpdateView.as_view(), name='request-user-update'),

    # Подтвердить код и обновить данные
    path('api/auth/users/<str:email>/confirm-update/', ConfirmUserUpdateView.as_view(), name='confirm-user-update'),

    # 🔹 Получение и обновление данных пользователя по email
    path('api/auth/users/<str:email>/', UserDetailView.as_view(), name='get-user-by-email'),

    # Новый эндпоинт получения перевалов пользователя
    path('api/auth/users/<str:email>/submits/', UserSubmitsView.as_view(), name='user-submits'),

    path("api/auth/users/<str:email>/confirm-update/", ConfirmUserUpdateView.as_view(), name="auth_users_confirm_update"),

    # Swagger и Redoc
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # Redoc UI
    re_path(r'^swagger.json$', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # JSON-схема API
]


# 📌 Дебаг-эндпоинты (временные)
def list_urls(request):
    """Возвращает JSON со списком всех маршрутов проекта."""
    urls = [str(url.pattern) for url in get_resolver().url_patterns]
    return JsonResponse({"routes": urls})


def check_admins(request):
    """Выводит список суперпользователей."""
    admins = User.objects.filter(is_superuser=True).values("username", "email")
    return JsonResponse({"superusers": list(admins)})


# Добавляем временные эндпоинты для дебага
urlpatterns += [
    path('debug/urls/', list_urls),  # Список маршрутов Django
    path('debug/admins/', check_admins),  # Список суперпользователей
]


# 📌 Подключение статических и медиа-файлов
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Если включен режим DEBUG, добавляем дополнительную обработку статики
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
