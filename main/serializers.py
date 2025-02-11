#  /Mountain Pass Application/main/serializers.py


import logging
from rest_framework import serializers
from main.models import PerevalAdded, Coords, User, PerevalImages, PerevalDifficulty

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


class PerevalDifficultySerializer(serializers.ModelSerializer):
    """Сериализатор уровня сложности"""
    class Meta:
        model = PerevalDifficulty
        fields = ['season', 'level']


class SubmitDataSerializer(serializers.ModelSerializer):
    """Сериализатор для входных данных API"""

    user = UserSerializer()  # Декодируем объект пользователя
    coord = CoordsSerializer()  # Декодируем объект координат
    difficulties = PerevalDifficultySerializer(many=True)  # Теперь список сложностей
    images = PerevalImagesSerializer(many=True, read_only=True)
    class Meta:
        model = PerevalAdded
        images = PerevalImagesSerializer(many=True, read_only=True)  # Связанное поле
        fields = ['beautyTitle', 'title', 'other_titles', 'connect', 'add_time', 'user', 'coord', 'status',
                  'difficulties', 'images']

    def create(self, validated_data):
        """Создание перевала с уровнями сложности"""
        difficulties_data = validated_data.pop('difficulties')  # Извлекаем уровни сложности
        pereval = PerevalAdded.objects.create(**validated_data)

        # Создаём записи сложности
        for diff_data in difficulties_data:
            PerevalDifficulty.objects.create(pereval=pereval, **diff_data)

        return pereval


