
# Mountain Pass Application

## Description
Mountain Pass Application is a REST API designed for managing mountain pass data for the Russian Sports Tourism Federation (FSTR).  
The system allows tourists to submit applications for passes, and enables moderators and administrators to process, moderate, and manage these applications efficiently.

## Problem
FSTR previously processed mountain pass applications manually, leading to delays of several months and inefficiencies for both tourists and staff.

## Solution
This project provides a Django REST API with JWT authentication to automate submission, review, and moderation of mountain pass data.  
The API includes secure access, role-based permissions, and full Swagger/ReDoc documentation for easy integration.

## Technologies
- Python 3.12
- Django 4.x
- Django REST Framework
- djangorestframework-simplejwt (JWT authentication)
- Swagger / ReDoc (API documentation)
- SQLite (local) / MySQL (production)

## Result
Reduced application processing time from several months to just a few days.  
Simplified data management for both tourists and FSTR staff.

---

## How to Use

### Run the server
1️⃣ Clone the repository:
```bash
git clone https://github.com/Rostislav62/Mountain-Pass-Application.git
cd Mountain-Pass-Application
```

2️⃣ Create and activate a virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate
```

3️⃣ Install dependencies:
```bash
pip install -r requirements.txt
```

4️⃣ Apply migrations and create a superuser:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5️⃣ Start the server:
```bash
python manage.py runserver
```
Access points:
- Swagger: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/

---

## API interfaces and example endpoints
### User roles
- **Guest:** read-only access
- **User:** can submit passes
- **Moderator:** can review, approve, or reject passes
- **Admin:** full access

### Main API endpoints

- List passes:
GET /submitData/list/
Example response:
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

- Add a new pass:
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

- Update pass:
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
- Delete pass:
DELETE /submitData/{id}/delete/
✅ Admin can delete anything
✅ Moderator can delete if status is new
✅ User can delete their own pass if status is new

- Get pass info:
GET /submitData/{id}/info/

- Update moderation status:
PUT /moderation/{id}/decision/
```json
    {
      "status_id": 3
    }
```
3 – Approved
4 – Rejected

- List passes with pending status::
GET /moderation/


## License
MIT License  
© 2025 Rostislav
