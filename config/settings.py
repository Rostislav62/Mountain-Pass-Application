#  /Mountain Pass Application/config/settings.py

from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv

import mimetypes
from django.apps import apps

load_dotenv(find_dotenv())  # Загружаем переменные из .env

mimetypes.add_type("application/json", ".json", True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-err^oskgs2y1-p8x4v6c418r22dk9n9p#d*%eyhj_$i4*o75m('

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False
# DEBUG = True
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

DEBUG_PROPAGATE_EXCEPTIONS = True  # Выводим полные ошибки в консоль

# # Для локального запускм
# ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

# ДЛя запуска на railway
# ALLOWED_HOSTS = [
#     "mountain-pass-application-production.up.railway.app",  # Продакшн-домен на Railway
#     "127.0.0.1",  # Локальный хост для разработки
#     "localhost",  # Используется для локального запуска Django
#     ".ngrok-free.app",  # Разрешает все поддомены Ngrok
# ]


# ДЛя запуска на pythonanywhere.com
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "rostislav62.pythonanywhere.com").split(",")

# CSRF_TRUSTED_ORIGINS = ["https://mountain-pass-application-production.up.railway.app"]
# CSRF_TRUSTED_ORIGINS = ['https://rostislav62.pythonanywhere.com']

# CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "https://rostislav62.pythonanywhere.com").split(",")


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'rest_framework',  # Подключаем DRF
    'main',
    'dotenv',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if os.path.exists(BASE_DIR / "static"):
    STATICFILES_DIRS = [BASE_DIR / "static"]
    # BASE_DIR / "staticfiles/drf-yasg/swagger-ui-dist",  # Добавляем путь к Swagger UI
else:
    STATICFILES_DIRS = []

ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TEST_RUNNER = "django.test.runner.DiscoverRunner"

MEDIA_URL = '/media/'  # URL для доступа к медиа-файлам
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Директория для сохранения медиа

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
STRAVA_API_KEY = os.getenv("STRAVA_API_KEY")
YANDEX_MAPS_API_KEY = os.getenv("YANDEX_MAPS_API_KEY")

# Database
# Для PostgreSQL
#
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'mountain_pass_db',
#         'USER': 'postgres',
#         'PASSWORD': '1',
#         'HOST': 'localhost',
#         'PORT': 5432,
#     }
# }


# Для Railway
# DATABASES = {
#     'default': dj_database_url.config(
#         default=os.getenv("DATABASE_URL"),
#         conn_max_age=600,
#         ssl_require=True  # Обязательно для Railway
#     )
# }

#  Для MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('FSTR_DB_NAME', 'default_db_name'),
        'USER': os.getenv('FSTR_DB_LOGIN', 'default_user'),
        'PASSWORD': os.getenv('FSTR_DB_PASS', 'default_pass'),
        'HOST': os.getenv('FSTR_DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('FSTR_DB_PORT', '3306'),
    }
}


def get_api_permissions():
    """Определяет, требует ли API авторизацию (запускается после загрузки моделей)"""
    try:
        if not apps.ready:  # Проверяем, загружены ли приложения Django
            return ['rest_framework.permissions.AllowAny']  # 🔓 API открыт по умолчанию

        ApiSettings = apps.get_model('main', 'ApiSettings')  # 🔥 Динамически загружаем модель
        settings_obj, created = ApiSettings.objects.get_or_create(id=1)

        if settings_obj.require_authentication:
            return ['rest_framework.permissions.IsAuthenticated']  # 🔒 Требует JWT
    except Exception as e:
        print(f"⚠ Ошибка получения настроек API: {e}")
        return ['rest_framework.permissions.AllowAny']  # 🔓 В случае ошибки API открыт

    return ['rest_framework.permissions.AllowAny']


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': get_api_permissions(),  # Теперь загружается правильно
    # 'rest_framework.permissions.AllowAny',         # Любые пользователи
    # 'rest_framework.permissions.IsAuthenticated',  # Только авторизованные пользователи
}

LOGIN_URL = "/admin/login/"

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'config.urls.schema_view',
    'USE_SESSION_AUTH': False,  # Отключаем стандартную авторизацию Django
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'DEFAULT_MODEL_RENDERING': 'example',  # Позволяет вводить данные в JSON-формате
    'SHOW_REQUEST_HEADERS': True,  # Показывает заголовки запросов
    'DOC_EXPANSION': 'list',  # Раскрывает список методов API
    'SUPPORTED_SUBMIT_METHODS': ["get", "post", "put", "patch", "delete"],
}

# Создаём папку для логов, если её нет
# LOGS_DIR = os.path.join(BASE_DIR, 'logs')
# if not os.path.exists(LOGS_DIR):
#     os.makedirs(LOGS_DIR)
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '{levelname} {asctime} {module} {message}',
#             'style': '{',
#         },
#         'simple': {
#             'format': '{levelname} {message}',
#             'style': '{',
#         },
#     },
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(LOGS_DIR, 'debug.log'),
#             'formatter': 'verbose',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['file', 'console'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#         'django.db.backends': {  # Логирование SQL-запросов
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': False,
#         },
#     },
# }
