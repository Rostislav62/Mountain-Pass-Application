#  /Mountain Pass Application/main/db_service.py

from main.models import User, PerevalAdded, PerevalImages, Coords, WeatherInfo, PerevalUser, PerevalStatus
# from main.models import PerevalGpsTracks, PerevalHistory, RelatedObjects
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist  # Для обработки ошибок, если перевала нет


class DatabaseService:
    """Класс для работы с базой данных"""

    @staticmethod
    def add_user(email, fam, name, otc, phone):
        """
        Получает пользователя по email или создаёт нового.

        :param email: Email пользователя.
        :param fam: Фамилия.
        :param name: Имя.
        :param otc: Отчество.
        :param phone: Телефон.
        :return: Объект пользователя.
        """
        try:
            # Проверяем, есть ли уже пользователь с таким email
            user = User.objects.get(email=email)
            return user  # Если пользователь уже существует, просто возвращаем его

        except ObjectDoesNotExist:
            # Если пользователя нет – создаём нового
            user = User.objects.create(email=email, fam=fam, name=name, otc=otc, phone=phone)
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

    # @staticmethod
    # def add_gps_track(pereval_id, track_url):
    #     """
    #     Добавляет GPS-трек (GPX/KML) для указанного перевала.
    #
    #     :param pereval_id: ID перевала, к которому привязываем GPS-трек.
    #     :param track_url: Ссылка (путь) на файл GPS-трека.
    #     :return: Объект GPS-трека или ошибка, если перевал не найден.
    #     """
    #
    #     try:
    #         # Пытаемся найти перевал в базе данных по ID
    #         pereval = PerevalAdded.objects.get(id=pereval_id)
    #
    #         # Создаём запись в таблице PerevalGpsTracks, привязывая к найденному перевалу
    #         gps_track = PerevalGpsTracks.objects.create(pereval=pereval, track_path=track_url)
    #
    #         # Возвращаем созданный объект GPS-трека
    #         return gps_track
    #
    #     except ObjectDoesNotExist:
    #         # Если перевал с указанным ID не найден, выбрасываем ошибку
    # #         raise ValueError(f"Перевал с ID {pereval_id} не найден в базе данных")
    #
    # @staticmethod
    # def add_pereval_history(user_email, pereval_id, pass_date, comments=None):
    #     """
    #     Добавляет запись о прохождении перевала.
    #
    #     :param user_email: Email пользователя, совершившего прохождение.
    #     :param pereval_id: ID перевала, который был пройден.
    #     :param pass_date: Дата прохождения перевала.
    #     :param comments: Дополнительные комментарии (необязательно).
    #     :return: Объект PerevalHistory или ошибка, если пользователь или перевал не найдены.
    #     """
    #
    #     try:
    #         # Пытаемся найти пользователя по email
    #         user = User.objects.get(email=user_email)
    #
    #         # Пытаемся найти перевал по ID
    #         pereval = PerevalAdded.objects.get(id=pereval_id)
    #
    #         # Создаём запись о прохождении перевала
    #         history_entry = PerevalHistory.objects.create(
    #             user=user,
    #             pereval=pereval,
    #             pass_date=pass_date,
    #             comments=comments
    #         )
    #
    #         # Возвращаем созданный объект истории прохождений
    #         return history_entry
    #
    #     except ObjectDoesNotExist as e:
    #         # Если пользователь или перевал не найдены, выбрасываем ошибку
    #         raise ValueError(f"Ошибка: {str(e)}")

    #
    # @staticmethod
    # def add_related_objects(pereval_id, related_name, related_type):
    #     """
    #     Добавляет связанный объект (гора, хребет и т. д.) для указанного перевала.
    #
    #     :param pereval_id: ID перевала, к которому привязываем объект.
    #     :param related_name: Название связанного объекта.
    #     :param related_type: Тип объекта ('mountain', 'ridge', 'other').
    #     :return: Объект RelatedObjects или ошибка, если перевал не найден.
    #     """
    #
    #     try:
    #         # Проверяем, существует ли перевал с таким ID
    #         pereval = PerevalAdded.objects.get(id=pereval_id)
    #
    #         # Создаём запись о связанном объекте
    #         related_object = RelatedObjects.objects.create(
    #             pereval=pereval,
    #             related_name=related_name,
    #             related_type=related_type
    #         )
    #
    #         return related_object
    #
    #     except ObjectDoesNotExist:
    #         raise ValueError(f"Перевал с ID {pereval_id} не найден в базе данных")

    @staticmethod
    @transaction.atomic
    def add_pereval(user_email, data):
        """
        Добавляет новый перевал в БД.
        """

        # Получаем данные пользователя
        user_data = data.get('user', {})
        user, created = PerevalUser.objects.get_or_create(email=user_email)

        # Если пользователь уже существовал – обновляем его данные
        if not created:
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Создаём координаты перевала
        coord_data = data.get('coord', {})
        coord = Coords.objects.create(**coord_data)

        # Получаем ID статуса из данных запроса (по умолчанию "New" = id 1)
        status_id = data.get('status', 1)

        # Ищем объект PerevalStatus по ID (если не найден, берём статус "New")
        status_obj = PerevalStatus.objects.get(id=status_id)

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