#  /Mountain Pass Application/main/db_service.py

from main.models import User, PerevalAdded, PerevalImages, PerevalGpsTracks, PerevalHistory, Coords
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist  # Для обработки ошибок, если перевала нет


class DatabaseService:
    """Класс для работы с базой данных"""

    @staticmethod
    def add_user(email, fam, name, otc, phone):
        """Добавляет нового пользователя или возвращает существующего"""
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'fam': fam, 'name': name, 'otc': otc, 'phone': phone}
        )
        return user

    @staticmethod
    def add_coords(latitude, longitude, height):
        """Добавляет координаты перевала"""
        coords = Coords.objects.create(latitude=latitude, longitude=longitude, height=height)
        return coords

    @staticmethod
    @transaction.atomic
    def add_pereval(user_email, data):
        """Добавляет новый перевал в БД"""
        user = DatabaseService.add_user(
            email=user_email,
            fam=data['fam'],
            name=data['name'],
            otc=data.get('otc', ''),
            phone=data['phone']
        )

        coords = DatabaseService.add_coords(
            latitude=data['coords']['latitude'],
            longitude=data['coords']['longitude'],
            height=data['coords']['height']
        )

        pereval = PerevalAdded.objects.create(
            user=user,
            coord=coords,
            beautyTitle=data['beauty_title'],
            title=data['title'],
            other_titles=data.get('other_titles', ''),
            connect=data.get('connect', ''),
            status='new',
            level_winter=data['level'].get('winter', ''),
            level_summer=data['level'].get('summer', ''),
            level_autumn=data['level'].get('autumn', ''),
            level_spring=data['level'].get('spring', ''),
            route_description=data.get('route_description', ''),
            hazards=data.get('hazards', '')
        )

        for image in data.get('images', []):
            PerevalImages.objects.create(pereval=pereval, image_path=image['data'])

        return pereval

    @staticmethod
    def add_image(pereval_id, image_url):
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
            image = PerevalImages.objects.create(pereval=pereval, image_path=image_url)

            # Возвращаем созданный объект изображения
            return image

        except ObjectDoesNotExist:
            # Если перевал с указанным ID не найден, выбрасываем ошибку
            raise ValueError(f"Перевал с ID {pereval_id} не найден в базе данных")

    @staticmethod
    def add_gps_track(pereval_id, track_url):
        """
        Добавляет GPS-трек (GPX/KML) для указанного перевала.

        :param pereval_id: ID перевала, к которому привязываем GPS-трек.
        :param track_url: Ссылка (путь) на файл GPS-трека.
        :return: Объект GPS-трека или ошибка, если перевал не найден.
        """

        try:
            # Пытаемся найти перевал в базе данных по ID
            pereval = PerevalAdded.objects.get(id=pereval_id)

            # Создаём запись в таблице PerevalGpsTracks, привязывая к найденному перевалу
            gps_track = PerevalGpsTracks.objects.create(pereval=pereval, track_path=track_url)

            # Возвращаем созданный объект GPS-трека
            return gps_track

        except ObjectDoesNotExist:
            # Если перевал с указанным ID не найден, выбрасываем ошибку
            raise ValueError(f"Перевал с ID {pereval_id} не найден в базе данных")

    @staticmethod
    def add_pereval_history(user_email, pereval_id, pass_date, comments=None):
        """
        Добавляет запись о прохождении перевала.

        :param user_email: Email пользователя, совершившего прохождение.
        :param pereval_id: ID перевала, который был пройден.
        :param pass_date: Дата прохождения перевала.
        :param comments: Дополнительные комментарии (необязательно).
        :return: Объект PerevalHistory или ошибка, если пользователь или перевал не найдены.
        """

        try:
            # Пытаемся найти пользователя по email
            user = User.objects.get(email=user_email)

            # Пытаемся найти перевал по ID
            pereval = PerevalAdded.objects.get(id=pereval_id)

            # Создаём запись о прохождении перевала
            history_entry = PerevalHistory.objects.create(
                user=user,
                pereval=pereval,
                pass_date=pass_date,
                comments=comments
            )

            # Возвращаем созданный объект истории прохождений
            return history_entry

        except ObjectDoesNotExist as e:
            # Если пользователь или перевал не найдены, выбрасываем ошибку
            raise ValueError(f"Ошибка: {str(e)}")
