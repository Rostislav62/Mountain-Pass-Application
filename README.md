Mountain Pass Application

Mountain Pass Application – это REST API для регистрации и просмотра информации о горных перевалах.
Проект позволяет пользователям добавлять данные о перевалах, редактировать их и просматривать статусы модерации.

Функционал API
•	Регистрация перевалов
•	Редактирование перевалов (если статус new)
•	Просмотр статусов модерации
•	Получение списка всех отправленных пользователем перевалов
•	Swagger-документация API

Разворачивание локально

1.	Клонирование репозитория
git clone https://github.com/Rostislav62/Mountain-Pass-Application.git
cd Mountain-Pass-Application

2.	Установка зависимостей и запуск сервера
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate      # Для Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

После запуска сервер доступен по адресу:
http://127.0.0.1:8000/

Документация API
Swagger UI позволяет тестировать API в браузере.

Продакшен:
https://mountain-pass-application-production.up.railway.app/swagger/

Локально:
http://127.0.0.1:8000/swagger/

ReDoc:
https://mountain-pass-application-production.up.railway.app/redoc/

Как тестировать API в Postman
1.	Открыть Postman
2.	Добавить новый запрос, ввести URL и метод (GET, POST, PATCH)
3.	Перейти во вкладку "Body", выбрать raw, затем JSON
4.	Ввести JSON-данные запроса
5.	Нажать "Send"

Примеры API-запросов

Создание нового перевала (POST /api/submitData/)
URL:
https://mountain-pass-application-production.up.railway.app/api/submitData/
Тело запроса (JSON):
{
    "beautyTitle": "пер. ",
    "title": "Пхия",
    "other_titles": "Триев",
    "connect": "",
    "add_time": "2025-02-17T12:00:00Z",
    "user": {
        "email": "test@example.com",
        "fam": "Иванов",
        "name": "Пётр",
        "otc": "Александрович",
        "phone": "+79999999999"
    },
    "coord": {
        "latitude": "45.3842",
        "longitude": "7.1525",
        "height": "1200"
    },
    "difficulties": [],
    "images": []
}

Ответ (JSON):
{
    "status": 200,
    "message": null,
    "id": 1
}

Получение списка перевалов пользователя (GET /api/submitData/?user__email=)
URL:
https://mountain-pass-application-production.up.railway.app/api/submitData/?user__email=test@example.com
Ответ (JSON):
[
    {
        "beautyTitle": "пер. ",
        "title": "Пхия",
        "other_titles": "Триев",
        "connect": "",
        "add_time": "2025-02-18T12:33:19.985902Z",
        "user": {
            "id": 1,
            "fam": "Иванов",
            "name": "Пётр",
            "phone": "+79999999999",
            "otc": "Александрович"
        },
        "coord": {
            "id": 1,
            "latitude": "45.384200",
            "longitude": "7.152500",
            "height": 1200
        },
        "status": "new",
        "difficulties": [],
        "images": []
    }
]

Редактирование перевала (PATCH /api/submitData/<id>/)
URL:
https://mountain-pass-application-production.up.railway.app/api/submitData/1/
Тело запроса (JSON):
{
    "title": "Новый Пхия",
    "connect": "Долина реки Ингуш"
}

Ответ (JSON):
{
    "state": 1,
    "message": "Данные успешно обновлены"
}


Контакты
Email: smigliuc@mail.ru
GitHub: https://github.com/Rostislav62/Mountain-Pass-Application

