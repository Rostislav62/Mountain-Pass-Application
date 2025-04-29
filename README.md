# Mountain Pass Application

## Overview

### Problem
The Russian Sports Tourism Federation (FSTR) relies on manual processing for mountain pass applications, causing delays of several months.

### Solution
A Django-based REST API to streamline registration, editing, and moderation of mountain pass data, reducing processing time to days.

### Impact
Enhances efficiency for tourists and FSTR staff, improving application handling and user experience.

## About the Project
Mountain Pass Application is a REST API developed for the FSTR to manage mountain pass data. Users can submit, edit, and track pass applications, while moderators and admins handle approvals. The system features a role-based access model and comprehensive Swagger/OpenAPI documentation for easy integration.

This project showcases my skills in building scalable backend systems with Django, REST APIs, and secure authentication.

## Features
- **CRUD Operations**: Create, read, update, and delete pass records (restricted by moderation status).
- **Role-Based Access**:
  - Guests: Read-only access.
  - Users: Submit and edit passes before moderation.
  - Moderators: Approve or reject passes.
  - Admins: Full access, including deletion.
- **JWT Authentication**: Secure access with access/refresh tokens.
- **Moderation Workflow**: Track pass status (new, pending, approved, rejected).
- **API Documentation**: Swagger UI and Redoc for seamless integration.
- **Database**: SQLite (local) or PostgreSQL (production).

## How It Works
1. Users authenticate via JWT (`POST /api/auth/login/`) to obtain tokens.
2. Users submit pass data (`POST /submitData/`) with details like coordinates, images, and difficulty levels.
3. Moderators review pending passes (`GET /moderation/`) and update statuses (`PUT /moderation/{id}/decision/`).
4. Users track pass status (`GET /submitData/{id}/info/`).
5. Admins manage all data with full access.

## Technologies
- **Python 3.10**: Core language.
- **Django 4.x**: Web framework.
- **Django REST Framework**: API development.
- **JWT (djangorestframework-simplejwt)**: Authentication.
- **SQLite/PostgreSQL**: Database storage.
- **Swagger/OpenAPI**: API documentation.
- **Git**: Version control.

## Installation
1. Clone the repository:
   git clone https://github.com/Rostislav62/Mountain-Pass-Application.git
   cd Mountain-Pass-Application

2. Install dependencies:
pip install -r requirements.txt

3. Apply migrations and create a superuser:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

4. Run the server:
python manage.py runserver

The API will be available at http://127.0.0.1:8000/.

## Usage
. Authentication: Obtain a JWT token via:
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

Use the token in the Authorization header: Bearer <jwt_access_token>.

. Key Endpoints:
 . List passes: GET /submitData/list/
 . Create pass: POST /submitData/
 . Update pass: PATCH /submitData/{id}/update/
 . Delete pass: DELETE /submitData/{id}/delete/
 . Get pass details: GET /submitData/{id}/info/
 . Update moderation status: PUT /moderation/{id}/decision/
 . List pending passes: GET /moderation/

. API Documentation:
 . Local: Swagger or Redoc
 . Hosted: Swagger

## Example API Request
Create a new pass:

curl -X POST https://rostislav62.pythonanywhere.com/submitData/ \
  -H "Authorization: Bearer <jwt_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "beautyTitle": "Sunny Pass",
    "title": "Sunny Pass",
    "other_titles": "Sunlit Pass",
    "connect": true,
    "user": {
      "family_name": "Ivanov",
      "first_name": "Alexey",
      "father_name": "Sergeevich",
      "phone": "+79160000001",
      "email": "user1@example.com"
    },
    "coord": {
      "latitude": 43.123456,
      "longitude": 76.987654,
      "height": 2500
    },
    "status": 1,
    "difficulties": [{"season": 1, "difficulty": 3}],
    "images": [{"data": "image_url_1.jpg", "title": "Pass View"}]
  }'

## Demo
Explore the live API: https://rostislav62.pythonanywhere.com/swagger/

## Author
Rostislav — AI agent and backend developer. This project is part of my portfolio, showcasing expertise in REST API design, authentication, and database management.

## License
MIT License





 
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
GET/submitData/list/

Пример ответа:
{
    "beautyTitle": "Ледяной путь",
    "title": "Перевал Ледяной",
    "other_titles": "Ледяной перевал",
    "connect": true,
    "add_time": "2025-02-26T20:21:33.766892Z",
    "user": {
      "id": 14,
      "family_name": "Сидоров",
      "first_name": "Максим",
      "father_name": "Владимирович",
      "phone": "+79160000003",
      "email": "user3@example.com"
    },
    "coord": {
      "id": 11,
      "latitude": 42.876543,
      "longitude": 75.123456,
      "height": 3000
    },
    "status": 1,
    "difficulties": [],
    "images": [
      {
        "id": 7,
        "data": "image_url_3.jpg",
        "title": "Вечерний перевал"
      }
    ]
  },
  {


Добавление нового перевала:
POST/submitData/
{
  "beautyTitle": "Горный проход",
  "title": "Перевал Солнечный",
  "other_titles": "Солнечный перевал",
  "connect": true,
  "user": {
    "family_name": "Иванов",
    "first_name": "Алексей",
    "father_name": "Сергеевич",
    "phone": "+79160000001",
    "email": "user1@example.com"
  },
  "coord": {
    "latitude": 43.123456,
    "longitude": 76.987654,
    "height": 2500
  },
  "status": 1,
  "difficulties": [
    {
      "season": 1,
      "difficulty": 3
    }
  ],
  "images": [
    {
      "data": "image_url_1.jpg",
      "title": "Вид с перевала"
    }
  ]
}

Редактирование перевала:
PATCH/submitData/{id}/update/
{
  "beautyTitle": "Горный проход",
  "title": "Перевал Солнечный",
  "other_titles": "Солнечный перевал",
  "coord": {
    "latitude": 43.123456,
    "longitude": 76.987654,
    "height": 2500
  },
  "difficulties": [
    {
      "season": 1,
      "difficulty": 3
    }
  ]
}

Удаление перевала:
DELETE/submitData/{id}/delete/
Удаляет перевал по ID, если статус new
✅ Админ (IsSuperAdmin) может удалять всё.
✅ Модератор (IsModerator) может удалять, только если статус new.
✅ Обычный пользователь может удалить свой перевал, пока он в статусе new.


Получение информации о конкретном перевале по ID.
GET/submitData/{id}/info/


Обновление статуса модерации:
PUT/moderation/{id}/decision/
{
  "status_id": 3
}
3 – Approved 
4 - Rejected


Возвращает список перевалов со статусом pending:
GET/moderation/



Примеры вызова API с хостинга (PythonAnywhere)
Ниже приведены примеры запросов и ответов для основных методов API. В запросах используется базовый URL:
https://rostislav62.pythonanywhere.com


Дополнительная информация
Документация API доступна через Swagger UI по адресу:
Локально: http://127.0.0.1:8000/swagger/
http://127.0.0.1:8000/ redoc /
На сервере: https://rostislav62.pythonanywhere.com/swagger/
https://rostislav62.pythonanywhere.com/redoc/

Также доступна OpenAPI (JSON) схема по адресу:
Локально: http://127.0.0.1:8000/schema/?format=openapi
На сервере: https://rostislav62.pythonanywhere.com/ schema/?format=openapi


