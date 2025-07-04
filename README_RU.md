
# Mountain Pass Application

## Описание
Mountain Pass Application — это REST API для управления данными о горных перевалах, разработанное для нужд Федерации спортивного туризма России (ФСТР).  
Система позволяет туристам подавать заявки на прохождение перевалов, а модераторам и администраторам — обрабатывать эти заявки, модерировать данные и управлять ими.

## Проблема
ФСТР ранее обрабатывала заявки вручную, что приводило к задержкам на несколько месяцев. Это затрудняло работу туристов и сотрудников.

## Решение
Создан REST API на Django с JWT-аутентификацией, который автоматизирует процесс подачи, проверки и модерации заявок.  
API предоставляет защищённый доступ, ролевую модель и интеграцию со Swagger / ReDoc для документации.

## Технологии
- Python 3.12
- Django 4.x
- Django REST Framework
- djangorestframework-simplejwt (JWT authentication)
- Swagger / ReDoc (документация API)
- SQLite (локально) / MySQL (на сервере)

## Результат
Сокращение времени обработки заявок с нескольких месяцев до нескольких дней.  
Упрощение взаимодействия туристов и сотрудников ФСТР с данными о перевалах.

---

## Как использовать

### Запуск сервера
1️⃣ Клонировать проект:
```bash
git clone https://github.com/Rostislav62/Mountain-Pass-Application.git
cd Mountain-Pass-Application
```

2️⃣ Создать и активировать виртуальное окружение:
```bash
python3.12 -m venv venv
source venv/bin/activate
```

3️⃣ Установить зависимости:
```bash
pip install -r requirements.txt
```

4️⃣ Применить миграции и создать суперпользователя:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5️⃣ Запустить сервер:
```bash
python manage.py runserver
```
Доступ:
- Swagger: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/

---

## API интерфейсы и примеры вызовов

Токен необходимо передавать в заголовке Authorization:
```
Authorization: Bearer jwt_access_token
```

### Роли пользователей
- **Гость:** только чтение данных
- **Пользователь:** добавление перевалов
- **Модератор:** проверка, одобрение и отклонение перевалов
- **Администратор:** полный доступ ко всем функциям

### Основные API-эндпоинты

- Получение списка перевалов:
GET /submitData/list/
Пример ответа:
```json
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
    }
```

 - Добавление нового перевала:
POST /submitData/
```json
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
```

- Редактирование перевала:
PATCH /submitData/{id}/update/
```json

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
```
- Удаление перевала:
DELETE /submitData/{id}/delete/
✅ Админ может удалять всё
✅ Модератор может удалять только если статус new
✅ Пользователь может удалить свой перевал, пока он в статусе new

- Получение информации о перевале:
GET /submitData/{id}/info/

- Обновление статуса модерации:
PUT /moderation/{id}/decision/
```json
    {
      "status_id": 3
    }
```
3 – Approved
4 – Rejected

- Список перевалов со статусом pending:
GET /moderation/


## Лицензия
MIT License  
© 2025 Rostislav
