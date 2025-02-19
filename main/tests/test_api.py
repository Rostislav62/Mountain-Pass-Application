#  /Mountain Pass Application/main/tests/test_api.py
# from main.models import PerevalGpsTracks  # Импортируем модели
import pytest
from rest_framework.test import APIClient, APITestCase  # Импортируем клиент для тестирования API
from django.urls import reverse  # Импортируем reverse для получения URL маршрутов
from main.models import PerevalAdded, PerevalImages, Coords, User  # Импортируем модели
from rest_framework import status


@pytest.mark.django_db  # Указываем, что тесты используют тестовую базу данных
class TestAPI:
    """Тестирование API"""

    def setup_method(self):
        """Подготавливаем тестовый клиент перед каждым тестом"""

        self.client = APIClient()  # Создаём тестовый клиент для API
        self.submit_url = reverse("submit-data")

        # Получаем URL для отправки данных перевала
        self.upload_image_url = reverse("upload-image")  # Получаем URL для загрузки изображения
        # self.upload_track_url = reverse("upload-track")  # Получаем URL для загрузки GPS-трека

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
            "coord": {
                "latitude": "45.3842",
                "longitude": "7.1525",
                "height": "1200"
            },
            "level_winter": "",
            "level_summer": "1А",
            "level_autumn": "1А",
            "level_spring": "",
            "images": [],
            "difficulties": []
        }
        print("📤 Отправляем JSON в API:", payload)  # ✅ Логируем перед отправкой
        # Отправляем POST-запрос на создание перевала
        response = self.client.post(self.submit_url, data=payload, format="json")
        print("🔍 Ответ сервера:", response.status_code, response.json())  # ✅ Логируем ответ

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

    # def test_upload_track(self, tmp_path):
    #     """Тест: загрузка GPS-трека"""
    #
    #     # Создаём объект координат
    #     coords = Coords.objects.create(latitude=45.0, longitude=7.0, height=1000)
    #
    #     # Создаём тестовый перевал с тестовым пользователем
    #     pereval = PerevalAdded.objects.create(
    #         user=self.user,  # Указываем тестового пользователя
    #         coord=coords,
    #         beautyTitle="пер. ",
    #         title="Тестовый перевал"
    #     )
    #
    #     # Создаём временный GPX-файл в тестовой директории
    #     track_path = tmp_path / "test.gpx"
    #     track_path.write_bytes(b"<gpx></gpx>")  # Записываем тестовые данные в файл
    #
    #     # Открываем файл и отправляем его в API
    #     with open(track_path, "rb") as track_file:
    #         response = self.client.post(self.upload_track_url, {"track": track_file, "pereval_id": pereval.id})
    #
    #     # Проверяем, что сервер вернул код 201 (Created), а не 200
    #     assert response.status_code == 201
    #     assert response.json()["status"] == 200  # Проверяем успешный статус API
    #     assert PerevalGpsTracks.objects.count() == 1  # Проверяем, что GPS-трек добавлен в БД

@pytest.mark.django_db
class TestSubmitDataAPI:
    """Тестирование API для получения списка перевалов пользователя"""

    def setup_method(self):
        """Подготовка тестовых данных перед каждым тестом"""
        self.client = APIClient()

        # Создаём тестового пользователя
        self.user = User.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Пётр",
            otc="Александрович",
            phone="+79999999999"
        )

        # Создаём тестовые координаты
        self.coords = Coords.objects.create(latitude=45.0, longitude=7.0, height=1200)

        # Создаём несколько тестовых перевалов
        self.pereval1 = PerevalAdded.objects.create(user=self.user, coord=self.coords, title="Перевал 1", connect="Долина 1")
        self.pereval2 = PerevalAdded.objects.create(user=self.user, coord=self.coords, title="Перевал 2", connect="Долина 2")

    def test_get_perevals_by_user(self):
        """Тест получения списка перевалов по email пользователя"""
        url = reverse('submit-data-list') + f"?user__email={self.user.email}"
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)  # Проверяем, что пришёл список
        assert len(response.json()) > 0  # Проверяем, что список не пустой


class TestGetPerevalById(APITestCase):
    """Тестирование эндпоинта GET /submitData/<id>/"""

    def setUp(self):
        """Создаём тестовые данные перед тестированием"""
        self.user = User.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Пётр",
            otc="Александрович",
            phone="+79999999999"
        )

        self.coords = Coords.objects.create(latitude=45.0, longitude=7.0, height=1200)

        self.pereval = PerevalAdded.objects.create(
            user=self.user,
            coord=self.coords,
            beautyTitle="пер. ",
            title="Тестовый перевал",
            other_titles="Альтернативное название",
            connect="Долина реки",
            status="new"
        )

        self.url = reverse("submit-data-detail", kwargs={"pk": self.pereval.id})  # ✅ Проверяем имя эндпоинта

    def test_get_pereval_by_id(self):
        """Проверяем получение информации о перевале по id"""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Тестовый перевал"


from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from main.models import PerevalAdded, User, Coords

class TestUpdatePereval(APITestCase):
    """Тестирование PATCH /submitData/<id>/update/"""

    def setUp(self):
        """Создаём тестовые данные перед тестированием"""
        self.user = User.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Пётр",
            otc="Александрович",
            phone="+79999999999"
        )

        self.coords = Coords.objects.create(latitude=45.0, longitude=7.0, height=1200)

        self.pereval = PerevalAdded.objects.create(
            user=self.user,
            coord=self.coords,
            beautyTitle="пер. ",
            title="Тестовый перевал",
            other_titles="Альтернативное название",
            connect="Долина реки",
            status="new"  # Только new можно редактировать
        )

        self.url = reverse("submit-data-update", kwargs={"pk": self.pereval.id})  # ✅ Используем правильный маршрут

    def test_patch_pereval(self):
        """Проверяем обновление данных о перевале"""
        payload = {
            "title": "Обновлённый перевал",
            "connect": "Обновлённое соединение"
        }

        response = self.client.patch(self.url, data=payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["state"] == 1  # Успешное обновление

        # Проверяем, что данные изменились
        self.pereval.refresh_from_db()
        assert self.pereval.title == "Обновлённый перевал"
        assert self.pereval.connect == "Обновлённое соединение"


from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from main.models import PerevalAdded, User, Coords

class TestGetPerevalsByUser(APITestCase):
    """Тестирование GET /submitData/?user__email=<email>/"""

    def setUp(self):
        """Создаём тестовые данные перед тестированием"""
        self.user = User.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Пётр",
            otc="Александрович",
            phone="+79999999999"
        )

        self.coords = Coords.objects.create(latitude=45.0, longitude=7.0, height=1200)

        # Создаём несколько тестовых перевалов для пользователя
        self.pereval1 = PerevalAdded.objects.create(
            user=self.user,
            coord=self.coords,
            beautyTitle="пер. ",
            title="Первый перевал",
            other_titles="Альтернативное название 1",
            connect="Долина реки 1",
            status="new"
        )

        self.pereval2 = PerevalAdded.objects.create(
            user=self.user,
            coord=self.coords,
            beautyTitle="пер. ",
            title="Второй перевал",
            other_titles="Альтернативное название 2",
            connect="Долина реки 2",
            status="new"
        )

        self.url = reverse("submit-data-list") + f"?user__email={self.user.email}"

    def test_get_perevals_by_user(self):
        """Проверяем получение списка перевалов пользователя по email"""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2  # Проверяем, что вернулись 2 перевала
        assert response.json()[0]["title"] == "Первый перевал"
        assert response.json()[1]["title"] == "Второй перевал"
