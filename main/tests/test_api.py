#  /Mountain Pass Application/main/tests/test_api.py

import pytest
from rest_framework.test import APIClient  # Импортируем клиент для тестирования API
from django.urls import reverse  # Импортируем reverse для получения URL маршрутов
from main.models import PerevalAdded, PerevalImages, PerevalGpsTracks, Coords, User  # Импортируем модели

@pytest.mark.django_db  # Указываем, что тесты используют тестовую базу данных
class TestAPI:
    """Тестирование API"""

    def setup_method(self):
        """Подготавливаем тестовый клиент перед каждым тестом"""

        self.client = APIClient()  # Создаём тестовый клиент для API
        self.submit_url = reverse("submit-data")  # Получаем URL для отправки данных перевала
        self.upload_image_url = reverse("upload-image")  # Получаем URL для загрузки изображения
        self.upload_track_url = reverse("upload-track")  # Получаем URL для загрузки GPS-трека

        # Создаём тестового пользователя, который будет использоваться в тестах
        self.user = User.objects.create(
            email="testuser@example.com",
            fam="Тестов",
            name="Тест",
            otc="Тестович",
            phone="+79998887766"
        )

    def test_submit_valid_data(self):
        """Тест: корректные данные создают запись в БД"""

        payload = {
            "beautyTitle": "пер. ",
            "title": "Пхия",
            "other_titles": "Триев",
            "connect": "",
            "add_time": "2024-06-15T12:00:00Z",
            "user": {
                "email": self.user.email,  # Используем тестового пользователя
                "fam": self.user.fam,
                "name": self.user.name,
                "otc": self.user.otc,
                "phone": self.user.phone
            },
            "coords": {
                "latitude": "45.3842",
                "longitude": "7.1525",
                "height": "1200"
            },
            "level_winter": "",
            "level_summer": "1А",
            "level_autumn": "1А",
            "level_spring": "",
            "images": []
        }

        # Отправляем POST-запрос на создание перевала
        response = self.client.post(self.submit_url, data=payload, format="json")

        # Проверяем, что сервер вернул код 201 (Created)
        assert response.status_code == 201
        assert response.json()["status"] == 200  # Проверяем, что API вернул успешный статус
        assert PerevalAdded.objects.count() == 1  # Проверяем, что в БД создана одна запись

    def test_upload_image(self, tmp_path):
        """Тест: загрузка изображения"""

        # Создаём объект координат
        coords = Coords.objects.create(latitude=45.0, longitude=7.0, height=1000)

        # Создаём тестовый перевал с тестовым пользователем
        pereval = PerevalAdded.objects.create(
            user=self.user,  # Указываем тестового пользователя
            coord=coords,
            beautyTitle="пер. ",
            title="Тестовый перевал"
        )

        # Создаём временный файл изображения в тестовой директории
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"testimagecontent")  # Записываем тестовые данные в файл

        # Открываем файл и отправляем его в API
        with open(image_path, "rb") as image_file:
            response = self.client.post(self.upload_image_url, {"image": image_file, "pereval_id": pereval.id})

        # Проверяем, что сервер вернул код 201 (Created), а не 200
        assert response.status_code == 201
        assert response.json()["status"] == 200  # Проверяем успешный статус API
        assert PerevalImages.objects.count() == 1  # Проверяем, что изображение добавлено в БД

    def test_upload_track(self, tmp_path):
        """Тест: загрузка GPS-трека"""

        # Создаём объект координат
        coords = Coords.objects.create(latitude=45.0, longitude=7.0, height=1000)

        # Создаём тестовый перевал с тестовым пользователем
        pereval = PerevalAdded.objects.create(
            user=self.user,  # Указываем тестового пользователя
            coord=coords,
            beautyTitle="пер. ",
            title="Тестовый перевал"
        )

        # Создаём временный GPX-файл в тестовой директории
        track_path = tmp_path / "test.gpx"
        track_path.write_bytes(b"<gpx></gpx>")  # Записываем тестовые данные в файл

        # Открываем файл и отправляем его в API
        with open(track_path, "rb") as track_file:
            response = self.client.post(self.upload_track_url, {"track": track_file, "pereval_id": pereval.id})

        # Проверяем, что сервер вернул код 201 (Created), а не 200
        assert response.status_code == 201
        assert response.json()["status"] == 200  # Проверяем успешный статус API
        assert PerevalGpsTracks.objects.count() == 1  # Проверяем, что GPS-трек добавлен в БД
