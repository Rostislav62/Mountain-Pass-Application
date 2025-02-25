#  /Mountain Pass Application/main/serializers.py


import logging
from rest_framework import serializers
from main.models import PerevalAdded, Coords, User, PerevalImages, PerevalDifficulty, Season, DifficultyLevel, \
    ApiSettings


logger = logging.getLogger(__name__)  # Логируем данные для отладки




class CoordsSerializer(serializers.ModelSerializer):
    """Сериализатор для координат перевала"""

    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, coerce_to_string=False
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, coerce_to_string=False
    )
    height = serializers.IntegerField()

    class Meta:
        model = Coords
        fields = '__all__'

    def validate_latitude(self, value):
        """Проверяем, что широта в пределах допустимых значений"""
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Широта должна быть в пределах от -90 до 90.")
        return value

    def validate_longitude(self, value):
        """Проверяем, что долгота в пределах допустимых значений"""
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Долгота должна быть в пределах от -180 до 180.")
        return value

    def validate_height(self, value):
        """Проверяем, что высота в пределах допустимых значений"""
        if not (-500 <= value <= 9000):
            raise serializers.ValidationError("Высота должна быть в пределах от -500 до 9000 метров.")
        return value

    class Meta:
        model = Coords
        fields = '__all__'

    def update(self, instance, validated_data):
        """Обновляем данные пользователя и профиля"""
        profile_data = validated_data.pop('profile', {})
        instance = super().update(instance, validated_data)

        profile, created = UserProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance



class PerevalImagesSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений перевала"""

    class Meta:
        model = PerevalImages
        fields = ['id', 'data', 'title']


class PerevalDifficultySerializer(serializers.ModelSerializer):
    """Сериализатор уровня сложности"""

    season = serializers.PrimaryKeyRelatedField(queryset=Season.objects.all())  # Передаём ID
    difficulty = serializers.PrimaryKeyRelatedField(queryset=DifficultyLevel.objects.all())  # Передаём ID

    class Meta:
        model = PerevalDifficulty
        fields = ['season', 'difficulty']


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор стандартного пользователя Django"""

    class Meta:
        model = User  # Используем `auth.User`
        fields = ['id', 'username', 'email']


class SubmitDataSerializer(serializers.ModelSerializer):
    """Сериализатор для входных данных API"""

    user = UserSerializer()  # Декодируем объект пользователя
    coord = CoordsSerializer()  # Декодируем объект координат
    difficulties = PerevalDifficultySerializer(many=True)  # Теперь список сложностей

    images = PerevalImagesSerializer(many=True, required=True)

    class Meta:
        model = PerevalAdded
        fields = ['beautyTitle', 'title', 'other_titles', 'connect', 'add_time', 'user', 'coord', 'status',
                  'difficulties', 'images']

    def create(self, validated_data):
        difficulties_data = validated_data.pop('difficulties', [])
        images_data = validated_data.get('images', [])

        print("🔍 Полученные изображения в `create()`: ", images_data)  # Вывод в консоль
        print("Полученные изображения:", images_data)  # Вывод в консоль для проверки

        pereval = PerevalAdded.objects.create(**validated_data)

        # Создаём изображения (ДОЛЖНО БЫТЬ ИМЕННО ТАК!)
        for image_data in images_data:
            PerevalImages.objects.create(
                pereval=pereval,
                data=image_data.get("data", ""),  # Проверяем, передаётся ли data
                title=image_data.get("title", "")  # Проверяем, передаётся ли title
            )

        return pereval

    def update(self, instance, validated_data):
        """Оптимизированное обновление перевала"""

        user_data = validated_data.pop("user", None)
        coord_data = validated_data.pop("coord", None)
        difficulties_data = validated_data.pop('difficulties', [])
        images_data = validated_data.pop('images', [])

        # Обновляем пользователя
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Обновляем координаты
        if coord_data:
            for attr, value in coord_data.items():
                setattr(instance.coord, attr, value)
            instance.coord.save()

        # Обновляем сам перевал
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 🔥 Исправляем ошибку с `difficulties`
        instance.difficulties.all().delete()  # Удаляем старые данные
        new_difficulties = [PerevalDifficulty(pereval=instance, **diff) for diff in difficulties_data]
        PerevalDifficulty.objects.bulk_create(new_difficulties)  # Массовое создание

        # 🔥 Исправляем ошибку с `images`
        instance.images.all().delete()
        new_images = [PerevalImages(pereval=instance, **img) for img in images_data]
        PerevalImages.objects.bulk_create(new_images)

        return instance


class ApiSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор для настройки API"""

    class Meta:
        model = ApiSettings
        fields = ['require_authentication', 'updated_at', 'updated_by']
        read_only_fields = ['updated_at', 'updated_by']  # Эти поля нельзя изменять вручную



