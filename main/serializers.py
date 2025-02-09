#  /Mountain Pass Application/main/serializers.py


import logging
from rest_framework import serializers
from main.models import PerevalAdded, Coords, User, PerevalImages

logger = logging.getLogger(__name__)  # Логируем данные для отладки


class CoordsSerializer(serializers.ModelSerializer):
    """Сериализатор для координат перевала"""
    class Meta:
        model = Coords
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""

    email = serializers.EmailField(write_only=True)
    fam = serializers.CharField(required=True)  # Фамилия обязательна
    name = serializers.CharField(required=True)  # Имя обязательно
    phone = serializers.CharField(required=True)  # Телефон обязателен

    class Meta:
        model = User
        fields = '__all__'



    def create(self, validated_data):
        """Получаем пользователя по email или создаём нового"""
        user, created = User.objects.get_or_create(email=validated_data['email'], defaults=validated_data)
        return user


class PerevalImagesSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений перевала"""
    class Meta:
        model = PerevalImages
        fields = ['image_path']




class SubmitDataSerializer(serializers.ModelSerializer):
    """Сериализатор для входных данных API"""

    user = UserSerializer()
    coords = CoordsSerializer()
    images = PerevalImagesSerializer(many=True)

    class Meta:
        model = PerevalAdded
        fields = [
            'beautyTitle', 'title', 'other_titles', 'connect',
            'add_time', 'user', 'coords', 'status', 'level_winter',
            'level_summer', 'level_autumn', 'level_spring', 'images'
        ]

    def create(self, validated_data):
        """Обрабатываем создание перевала"""

        # Логируем входные данные для отладки
        logger.debug(f"validated_data: {validated_data}")

        user_data = validated_data.pop('user', None)

        # Если `user_data` отсутствует, вызываем ошибку
        if not user_data:
            raise serializers.ValidationError({"user": "Поле `user` обязательно"})

        # Проверяем, что ключи `fam`, `name`, `phone` есть в user_data
        required_fields = ['email', 'fam', 'name', 'phone']
        missing_fields = [field for field in required_fields if field not in user_data]
        if missing_fields:
            raise serializers.ValidationError({field: f"Поле `{field}` обязательно" for field in missing_fields})

        # Получаем пользователя или создаём нового
        user, _ = User.objects.get_or_create(email=user_data['email'], defaults=user_data)

        # Создаём координаты
        coords = Coords.objects.create(**validated_data.pop('coords'))

        # Создаём перевал
        pereval = PerevalAdded.objects.create(user=user, coord=coords, **validated_data)

        return pereval
