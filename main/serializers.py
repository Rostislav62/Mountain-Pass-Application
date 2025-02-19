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

    email = serializers.EmailField(write_only=True, required=True)
    fam = serializers.CharField(required=True)  # Фамилия обязательна
    name = serializers.CharField(required=True)  # Имя обязательно
    phone = serializers.CharField(required=True)  # Телефон обязателен

    class Meta:
        model = User
        fields = '__all__'

    def validate(self, data):
        print("📤 Данные перед валидацией в UserSerializer:", data)  # ✅ Логируем данные
        return data

    def create(self, validated_data):
        """Получаем пользователя по email или создаём нового"""
        user, created = User.objects.get_or_create(email=validated_data['email'], defaults=validated_data)
        return user


class PerevalImagesSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений перевала"""

    class Meta:
        model = PerevalImages
        fields = ['data', 'title']



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
        """Обновляем перевал"""
        user_data = validated_data.pop("user", None)  # Достаём `user`
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)  # Обновляем данные пользователя
            user.save()  # Сохраняем изменения

        return super().update(instance, validated_data)





