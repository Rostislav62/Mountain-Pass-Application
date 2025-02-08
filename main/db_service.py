

from main.models import User, PerevalAdded, PerevalImages, PerevalGpsTracks, PerevalHistory, Coords
from django.db import transaction

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
