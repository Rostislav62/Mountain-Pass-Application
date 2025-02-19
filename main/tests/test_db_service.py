#  /Mountain Pass Application/main/tests/test_db_service.py

import pytest
from django.test import TestCase
from main.db_service import DatabaseService
from main.models import User, PerevalAdded, Coords, PerevalImages, PerevalGpsTracks, PerevalHistory


@pytest.mark.django_db  # Используем тестовую БД
class TestDatabaseService(TestCase):

    def setUp(self):
        """Создаём тестовые данные перед запуском тестов"""
        self.user = User.objects.create(
            email="test@example.com",
            fam="Иванов",
            name="Пётр",
            otc="Александрович",
            phone="+79999999999"
        )
        self.coords = Coords.objects.create(latitude=45.3842, longitude=7.1525, height=1200)
        self.pereval = PerevalAdded.objects.create(
            user=self.user,
            coord=self.coords,
            beautyTitle="пер. ",
            title="Пхия",
            other_titles="Триев",
            connect="",
            status="new",
            level_winter="",
            level_summer="1А",
            level_autumn="1А",
            level_spring=""
        )

    def test_add_image(self):
        """Тестируем метод add_image"""
        image = DatabaseService.add_image(self.pereval.id, "https://example.com/image1.jpg")
        assert image.pereval == self.pereval
        assert image.image_path == "https://example.com/image1.jpg"

    def test_add_gps_track(self):
        """Тестируем метод add_gps_track"""
        gps_track = DatabaseService.add_gps_track(self.pereval.id, "https://example.com/track1.gpx")
        assert gps_track.pereval == self.pereval
        assert gps_track.track_path == "https://example.com/track1.gpx"

    def test_add_pereval_history(self):
        """Тестируем метод add_pereval_history"""
        history_entry = DatabaseService.add_pereval_history(
            user_email=self.user.email,
            pereval_id=self.pereval.id,
            pass_date="2024-06-15",
            comments="Отличный перевал!"
        )
        assert history_entry.pereval == self.pereval
        assert history_entry.user == self.user
        assert history_entry.comments == "Отличный перевал!"
