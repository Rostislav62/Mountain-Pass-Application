#  /Mountain Pass Application/main/db_service.py

from main.models import User, PerevalAdded, PerevalImages, Coords, PerevalUser, PerevalStatus
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist  # Для обработки ошибок, если перевала нет
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Класс для работы с базой данных"""

    @staticmethod
    def add_user(user_data):
        """🔍 Ищет пользователя по email или телефону. Если находит — возвращает, иначе создаёт нового."""

        logger.info(f"🔍 ШАГ 3.1: Поиск пользователя по email={user_data['email']} или phone={user_data['phone']}")
        print(f"🔍 ШАГ 3.1: Поиск пользователя по email={user_data['email']} или phone={user_data['phone']}")

        user = PerevalUser.objects.filter(email=user_data["email"]).first() or \
               PerevalUser.objects.filter(phone=user_data["phone"]).first()

        if user:
            logger.info(f"✅ ШАГ 3.2: Пользователь найден: {user}")
            return user

        logger.info("👤 ШАГ 3.3: Пользователь не найден, создаём нового")
        user = PerevalUser.objects.create(
            email=user_data["email"],
            phone=user_data["phone"],
            family_name=user_data["family_name"],
            first_name=user_data["first_name"],
            father_name=user_data.get("father_name", "")
        )
        logger.info(f"✅ ШАГ 3.4: Пользователь создан: {user}")
        return user

    @staticmethod
    def add_coords(latitude, longitude, height):
        """Добавляет координаты перевала"""
        coords = Coords.objects.create(latitude=latitude, longitude=longitude, height=height)
        return coords

    @staticmethod
    def add_image(pereval_id, data, title):
        """
        Добавляет изображение для указанного перевала.

        :param pereval_id: ID перевала, к которому привязываем изображение.
        :param image_url: Ссылка (путь) на изображение.
        :return: Объект изображения или ошибка, если перевал не найден.
        """

        try:
            # Пытаемся найти перевал в базе данных по ID
            pereval = PerevalAdded.objects.get(id=pereval_id)

            # Создаём запись в таблице PerevalImages, привязывая к найденному перевалу
            image = PerevalImages.objects.create(pereval=pereval, data=data, title=title)

            # Возвращаем созданный объект изображения
            return image

        except ObjectDoesNotExist:
            # Если перевал с указанным ID не найден, выбрасываем ошибку
            raise ValueError(f"Перевал с ID {pereval_id} не найден в базе данных")


    @staticmethod
    @transaction.atomic
    def add_pereval(user_email, data):
        logger.info(f"🏔️ ШАГ 6.1: Начало создания перевала для пользователя {user_email}")
        print(f"🏔️ ШАГ 6.1: Начало создания перевала для пользователя {user_email}")

        user = PerevalUser.objects.get(email=user_email)
        logger.info(f"👤 ШАГ 6.2: Найден пользователь (user_id={user.id})")
        print(f"👤 ШАГ 6.2: Найден пользователь (user_id={user.id})")

        coord_data = data.get('coord', {})
        coord = Coords.objects.create(**coord_data)
        logger.info(f"📍 ШАГ 6.3: Координаты созданы")

        difficulties_data = data.get('difficulties', [])

        pereval = PerevalAdded.objects.create(
            user_id=user.id,
            coord=coord,
            beautyTitle=data.get('beautyTitle', ''),
            title=data.get('title', ''),
            other_titles=data.get('other_titles', ''),
            connect=data.get('connect', False),
            status=data.get('status', 1),
            route_description=data.get('route_description', '')
        )
        logger.info(f"✅ ШАГ 7: Перевал успешно создан, ID: {pereval.id}")
        print(f"✅ ШАГ 7: Перевал успешно создан, ID: {pereval.id}")

        from main.models import PerevalDifficulty
        for diff in difficulties_data:
            PerevalDifficulty.objects.create(
                pereval=pereval,
                season_id=diff['season'],  # Используем ID
                difficulty_id=diff['difficulty']  # Используем ID
            )
            logger.info(f"✅ Создана сложность для перевала {pereval.id}")

        return pereval


    @staticmethod
    def get_weather(pereval_id):
        """
        Получает сохранённые данные о погоде для указанного перевала.

        :param pereval_id: ID перевала, для которого запрашивается погода.
        :return: Объект WeatherInfo или сообщение, если данных нет.
        """

        try:
            # Ищем запись о погоде для указанного перевала
            weather = WeatherInfo.objects.get(pereval_id=pereval_id)
            return {
                "temperature": weather.temperature,
                "wind_speed": weather.wind_speed,
                "precipitation": weather.precipitation,
                "weather_date": weather.weather_date.strftime("%Y-%m-%d %H:%M:%S")
            }
        except ObjectDoesNotExist:
            return {"message": f"Погодные данные для перевала с ID {pereval_id} отсутствуют"}
