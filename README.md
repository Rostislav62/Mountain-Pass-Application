Mountain Pass Application
Описание проекта
Mountain Pass Application представляет собой REST API для регистрации и просмотра информации о горных перевалах. Проект позволяет пользователям добавлять данные о перевалах, редактировать их (при условии, что перевал еще не отправлен на модерацию) и отслеживать статус модерации. Система предназначена для сокращения времени обработки заявок с нескольких месяцев до нескольких дней, что упрощает работу как туристов, так и сотрудников ФСТР.

Проект храниться на GhitHub ресурсе по адресу: 
https://github.com/Rostislav62/Mountain-Pass-Application

Установка и запуск

1.	Клонируйте репозиторий:
git clone https://github.com/your-repo/mountain-pass.git
cd mountain-pass

2.	Установите зависимости:
pip install -r requirements.txt

3.	Примените миграции и создайте суперпользователя:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

4.	Запустите сервер:
python manage.py runserver

После запуска сервер будет доступен по адресу http://127.0.0.1:8000/

Аутентификация и права доступа

Mountain Pass Application использует JWT-аутентификацию. Для получения токена выполните следующий запрос:
Запрос:
POST /api/auth/login/
Тело запроса:
{
  "username": "admin",
  "password": "your_password"
}

Ответ:
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}

Токен необходимо передавать в заголовке Authorization следующим образом:
Authorization: Bearer jwt_access_token

Пользователи имеют следующие роли и соответствующий уровень доступа:
•	Гость: только чтение данных.
•	Пользователь: добавление перевалов.
•	Модератор: проверка, одобрение и отклонение перевалов.
•	Администратор: полный доступ ко всем функциям.

Основные API-эндпоинты

Получение списка перевалов:
GET /api/passes/
Пример ответа:
[
  {
    "id": 1,
    "title": "Перевал Тестовый",
    "difficulty": "3A",
    "status": "pending"
  }
]

Добавление нового перевала:
POST /api/passes/
{
  "title": "Новый перевал",
  "difficulty": "2A",
  "coord": {
    "latitude": 42.1234,
    "longitude": 72.5678,
    "height": 1500
  }
}

Редактирование перевала:
PUT /api/passes/{id}/
Копировать
{
  "title": "Обновлённый перевал",
  "difficulty": "3B"
}

Удаление перевала:
DELETE /api/passes/{id}/

Обновление статуса модерации:
PUT /api/moderation/{id}/approve/

Получение информации о конкретном перевале:
GET /api/passes/{id}/

Примеры вызова API с хостинга (PythonAnywhere)
Ниже приведены примеры запросов и ответов для основных методов API. В запросах используется базовый URL:
https://rostislav62.pythonanywhere.com

Авторизация
1. Вход в систему (login)
Запрос:
POST https://rostislav62.pythonanywhere.com/api/auth/login/

Тело запроса:
{
  "username": "admin",
  "password": "1"
}
Идентификатор запроса: auth_login_create

2. Регистрация нового пользователя
Запрос:
POST https://rostislav62.pythonanywhere.com/api/auth/register/
Тело запроса:
{
  "username": "pepsX5CKweIv7Jgaxg1bqMuROJ_5BSyO4Wp8YOtrLYIDuz5",
  "email": "user@example.com",
  "profile": {
    "middle_name": "string",
    "phone": "string"
  }
}
Идентификатор запроса: auth_register_create

Работа с перевалами (submitData)

1. Получение списка перевалов пользователя по email
Запрос:
GET https://rostislav62.pythonanywhere.com/submitData/?user_email=user@example.com
Идентификатор запроса: submitData_list

2. Создание нового перевала
Запрос:
POST https://rostislav62.pythonanywhere.com/submitData/

Тело запроса:
{
  "beautyTitle": "string",
  "title": "string",
  "other_titles": "string",
  "connect": "string",
  "user": {
    "username": "bQ_pPt0IK8KoElaC",
    "email": "user@example.com",
    "profile": {
      "middle_name": "string",
      "phone": "string"
    }
  },
  "coord": {
    "latitude": 0,
    "longitude": 0,
    "height": 0
  },
  "status": "new",
  "difficulties": [
    {
      "season": 0,
      "difficulty": 0
    }
  ],
  "images": [
    {
      "data": "string",
      "title": "string"
    }
  ]
}
Идентификатор запроса: submitData_create

3. Получение списка всех перевалов, отправленных пользователем по email
Запрос:
GET https://rostislav62.pythonanywhere.com/submitData/list/
Идентификатор запроса: submitData_list_list

Пример ответа:
[
  {
    "beautyTitle": "string",
    "title": "string",
    "other_titles": "string",
    "connect": "string",
    "add_time": "2025-02-24T13:58:29.615Z",
    "user": {
      "id": 0,
      "username": "yMIvTNIprCO",
      "email": "user@example.com",
      "profile": {
        "middle_name": "string",
        "phone": "string"
      }
    },
    "coord": {
      "id": 0,
      "latitude": 0,
      "longitude": 0,
      "height": 0
    },
    "status": "new",
    "difficulties": [
      {
        "season": 0,
        "difficulty": 0
      }
    ],
    "images": [
      {
        "id": 0,
        "data": "string",
        "title": "string"
      }
    ]
  }
]

4. Редактирование перевала (частичное обновление)
Запрос:
PATCH https://rostislav62.pythonanywhere.com/submitData/{id}/
Идентификатор запроса: submitData_partial_update

5. Получение информации о конкретном перевале
Запрос:
GET https://rostislav62.pythonanywhere.com/submitData/{id}/info/
Идентификатор запроса: submitData_info_read


Загрузка изображений
Загрузка изображения для перевала
Запрос:
POST https://rostislav62.pythonanywhere.com/uploadImage/
Параметры:
•	pereval_id: integer (передается как параметр)
•	image: файл изображения (формат multipart/form-data)
Идентификатор запроса: uploadImage_create

Модерация

1. Получение списка перевалов со статусом pending
Запрос:
GET https://rostislav62.pythonanywhere.com/api/moderation/
Идентификатор запроса: api_moderation_list

Пример ответа:
[
  {
    "beautyTitle": "string",
    "title": "string",
    "other_titles": "string",
    "connect": "string",
    "add_time": "2025-02-24T14:07:46.489Z",
    "user": {
      "id": 0,
      "username": "Lvj_a3yJcdo9V93TE+G6rkbtX3ks9EdewOc9s3vDL.xfoCyn283MEYKh75uZnpBsW8fB5qu",
      "email": "user@example.com",
      "profile": {
        "middle_name": "string",
        "phone": "string"
      }
    },
    "coord": {
      "id": 0,
      "latitude": 0,
      "longitude": 0,
      "height": 0
    },
    "status": "new",
    "difficulties": [
      {
        "season": 0,
        "difficulty": 0
      }
    ],
    "images": [
      {
        "id": 0,
        "data": "string",
        "title": "string"
      }
    ]
  }
]

2. Одобрение перевала
Запрос:
PUT https://rostislav62.pythonanywhere.com/api/moderation/{id}/approve/
Идентификатор запроса: api_moderation_approve_update

3. Отклонение перевала
Запрос:
PUT https://rostislav62.pythonanywhere.com/api/moderation/{id}/reject/
Идентификатор запроса: api_moderation_reject_update

4. Отправка перевала на модерацию (смена статуса с new на pending)
Запрос:

PUT https://rostislav62.pythonanywhere.com/api/passes/{id}/submit/
Идентификатор запроса: api_passes_submit_update

Обновление и удаление перевалов
1. Полное обновление перевала
Запрос:
PUT https://rostislav62.pythonanywhere.com/api/passes/{id}/
Тело запроса:
{
  "beautyTitle": "string",
  "title": "string",
  "other_titles": "string",
  "connect": "string",
  "user": {
    "username": "4Vqxi2",
    "email": "user@example.com",
    "profile": {
      "middle_name": "string",
      "phone": "string"
    }
  },
  "coord": {
    "latitude": 0,
    "longitude": 0,
    "height": 0
  },
  "status": "new",
  "difficulties": [
    {
      "season": 0,
      "difficulty": 0
    }
  ],
  "images": [
    {
      "data": "string",
      "title": "string"
    }
  ]
}
Идентификатор запроса: api_passes_update

2. Частичное обновление перевала
Запрос:
PATCH https://rostislav62.pythonanywhere.com/api/passes/{id}/

Тело запроса:
json
Копировать
{
  "beautyTitle": "string",
  "title": "string",
  "other_titles": "string",
  "connect": "string",
  "user": {
    "username": "uK0NXE_6AETRIfl0YPWKbtfnS+7-EPZLr",
    "email": "user@example.com",
    "profile": {
      "middle_name": "string",
      "phone": "string"
    }
  },
  "coord": {
    "latitude": 0,
    "longitude": 0,
    "height": 0
  },
  "status": "new",
  "difficulties": [
    {
      "season": 0,
      "difficulty": 0
    }
  ],
  "images": [
    {
      "data": "string",
      "title": "string"
    }
  ]
}
Идентификатор запроса: api_passes_partial_update

3. Удаление перевала
Запрос:
DELETE https://rostislav62.pythonanywhere.com/api/passes/{id}/delete/
Идентификатор запроса: api_passes_delete_delete

Работа с фотографиями перевала

1. Получение списка фотографий перевала
Запрос:
GET https://rostislav62.pythonanywhere.com/api/passes/{id}/photos/
Идентификатор запроса: api_passes_photos_list

2. Удаление фотографии перевала
Запрос:
DELETE https://rostislav62.pythonanywhere.com/api/passes/{id}/photos/{photo_id}/delete/
Идентификатор запроса: api_passes_photos_delete_delete

Управление настройками API
1. Получение настроек API
Запрос:
GET https://rostislav62.pythonanywhere.com/api/settings/
Идентификатор запроса: api_settings_read

Пример ответа:
{
  "require_authentication": true,
  "updated_at": "2025-02-24T14:18:57.226Z",
  "updated_by": 0
}

2. Обновление настроек API (PUT)
Запрос:
PUT https://rostislav62.pythonanywhere.com/api/settings/

Тело запроса:
{
  "require_authentication": true
}
Идентификатор запроса: api_settings_update

3. Частичное обновление настроек API (PATCH)
Запрос:
PATCH https://rostislav62.pythonanywhere.com/api/settings/

Тело запроса:
{
  "require_authentication": true
}
Идентификатор запроса: api_settings_partial_update

Тестирование API
Для запуска всех тестов выполните команду:
python manage.py test

Тесты включают проверку основных эндпоинтов API (файлы test_api.py и test_db_service.py).


Дополнительная информация
Документация API доступна через Swagger UI по адресу:
Локально: http://127.0.0.1:8000/swagger/
http://127.0.0.1:8000/ redoc /
На сервере: https://rostislav62.pythonanywhere.com/swagger/
https://rostislav62.pythonanywhere.com/redoc/

Также доступна OpenAPI (JSON) схема по адресу:
Локально: http://127.0.0.1:8000/schema/?format=openapi
На сервере: https://rostislav62.pythonanywhere.com/ schema/?format=openapi


