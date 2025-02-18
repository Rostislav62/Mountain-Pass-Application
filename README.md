# 🏔️ Mountain Pass Application

**Mountain Pass Application** – это REST API для регистрации и просмотра информации о горных перевалах.  
Проект позволяет пользователям добавлять данные о перевалах, редактировать их, просматривать статусы модерации.

## 🚀 Функционал API

✅ Регистрация перевалов  
✅ Редактирование перевалов (если статус `new`)  
✅ Просмотр статусов модерации  
✅ Получение списка всех отправленных пользователем перевалов  
✅ Поддержка Swagger-документации  

---

## 🛠️ **Как развернуть локально**
### 🔹 **1. Клонировать репозиторий**
```bash
git clone https://github.com/your-username/mountain-pass-app.git
cd mountain-pass-app


Документация API
✅ Swagger UI:
🔗 https://mountain-pass-application-production.up.railway.app/swagger/

✅ ReDoc:
🔗 https://mountain-pass-application-production.up.railway.app/redoc/


Примеры API-запросов
🔹 1. Создание нового перевала (POST /api/submitData/)
📍 URL: https://mountain-pass-application-production.up.railway.app/api/submitData/
📥 Тело запроса (JSON):
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
📤 Ответ (JSON):
{
    "status": 200,
    "message": null,
    "id": 1
}

🔹 2. Получение списка перевалов пользователя (GET /api/submitData/?user__email=)
📍 URL: https://mountain-pass-application-production.up.railway.app/api/submitData/?user__email=test@example.com
📤 Ответ (JSON):
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

🔹 3. Редактирование перевала (PATCH /api/submitData/<id>/)
📍 URL: https://mountain-pass-application-production.up.railway.app/api/submitData/1/
📥 Тело запроса (JSON):
{
    "title": "Новый Пхия",
    "connect": "Долина реки Ингуш"
}

📤 Ответ (JSON):
{
    "state": 1,
    "message": "Данные успешно обновлены"
}

✨ Контакты
Разработчик:
📧 Email: test@example.com
🔗 GitHub: https://github.com/your-username/mountain-pass-app

