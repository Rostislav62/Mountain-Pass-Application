#  /Mountain Pass Application/main/db_service.py

from main.models import User, PerevalAdded, PerevalImages, Coords, WeatherInfo, PerevalUser, PerevalStatus
# from main.models import PerevalGpsTracks, PerevalHistory, RelatedObjects
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist  # Для обработки ошибок, если перевала нет


class DatabaseService:
    """Класс для работы с базой данных"""

    @staticmethod
    def add_user(user_data):
        """
        Ищет пользователя по email или телефону. Если находит — возвращает, иначе создаёт нового.
        """
        user = PerevalUser.objects.filter(email=user_data["email"]).first() or \
               PerevalUser.objects.filter(phone=user_data["phone"]).first()

        if user:
            return user  # Если пользователь найден, просто возвращаем его

        # Если пользователя нет – создаём нового
        return PerevalUser.objects.create(
            email=user_data["email"],
            phone=user_data["phone"],
            fam=user_data["family_name"],
            name=user_data["first_name"],
            otc=user_data.get("father_name", "")
        )

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
        """
        Добавляет новый перевал в БД.
        """

        # Получаем данные пользователя
        user_data = data.get('user', {})
        user, created = PerevalUser.objects.get_or_create(email=user_email, defaults=user_data)

        # Если пользователь уже существовал – обновляем его данные
        if not created:
            for attr, value in user_data.items():
                if value:  # Записываем только непустые значения
                    setattr(user, attr, value)
            user.save()

        # Создаём координаты перевала
        coord_data = data.get('coord', {})
        coord = Coords.objects.create(**coord_data)

        # Получаем ID статуса из данных запроса (по умолчанию "New" = id 1)
        status_id = data.get('status', 1)

        # Создаём перевал с объектом `PerevalStatus`
        pereval = PerevalAdded.objects.create(
            user=user,
            coord=coord,
            beautyTitle=data.get('beautyTitle', ''),
            title=data.get('title', ''),
            other_titles=data.get('other_titles', ''),
            connect=data.get('connect', ''),
            status=status_id,
        )

        images_data = data.get('images', [])
        for image_data in images_data:
            PerevalImages.objects.create(
                pereval=pereval,
                data=image_data.get("data", ""),
                title=image_data.get("title", "")
            )

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
