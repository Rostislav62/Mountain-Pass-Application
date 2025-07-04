#  /Mountain Pass Application/main/serializers.py


import logging
from rest_framework import serializers
from main.models import PerevalAdded, Coords, User, PerevalImages, PerevalDifficulty, Season, DifficultyLevel, \
    ApiSettings, PerevalUser, PerevalStatus
from django.contrib.auth.models import User
# from .serializers import PerevalUserSerializer, CoordsSerializer, SeasonSerializer, DifficultyLevelSerializer, \
#     PerevalDifficultySerializer, PerevalImagesSerializer

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
        """Обновляем данные пользователя"""
        return super().update(instance, validated_data)


class PerevalImagesSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений перевала"""

    class Meta:
        model = PerevalImages
        fields = ['id', 'data', 'title']

class PerevalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerevalUser
        fields = ['id', 'family_name', 'first_name', 'father_name', 'phone', 'email']

        
class DifficultyLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DifficultyLevel
        fields = ['code', 'description', 'characteristics', 'requirements']


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = ['code', 'name']


class PerevalDifficultySerializer(serializers.ModelSerializer):
    season = serializers.PrimaryKeyRelatedField(queryset=Season.objects.all())
    difficulty = serializers.PrimaryKeyRelatedField(queryset=DifficultyLevel.objects.all())

    class Meta:
        model = PerevalDifficulty
        fields = ['season', 'difficulty']


class SubmitDataSerializer(serializers.ModelSerializer):
    """📌 Сериализатор для модели PerevalAdded"""

    user = PerevalUserSerializer()  # 🔹 Сериализатор для пользователя
    coord = CoordsSerializer()  # 🔹 Сериализатор для координат
    status = serializers.PrimaryKeyRelatedField(queryset=PerevalStatus.objects.all())  # 🔹 Статус перевала
    difficulties = PerevalDifficultySerializer(many=True)  # 🔹 Сериализатор для сложностей
    images = PerevalImagesSerializer(many=True, required=True)  # 🔹 Сериализатор для изображений

    class Meta:
        model = PerevalAdded
        fields = [
            'id',
            'beautyTitle',
            'title',
            'other_titles',
            'connect',
            'add_time',
            'user',
            'coord',
            'status',
            'difficulties',
            'images',
            'route_description'
        ]

    def to_representation(self, instance):
        """📌 Преобразование объекта в JSON для чтения"""
        logger.info("[SubmitDataSerializer][to_representation] Преобразование объекта в JSON")
        representation = super().to_representation(instance)
        # 🔹 Заменяем difficulties на полные объекты для GET
        difficulties = instance.difficulties.all()
        representation['difficulties'] = [
            {
                'season': SeasonSerializer(diff.season).data,
                'difficulty': DifficultyLevelSerializer(diff.difficulty).data
            }
            for diff in difficulties
        ]
        logger.info("[SubmitDataSerializer][to_representation] Успешное преобразование")
        return representation

    def to_internal_value(self, data):
        """📌 Преобразование входных данных для записи"""
        logger.info("[SubmitDataSerializer][to_internal_value] Преобразование входных данных")
        ret = super().to_internal_value(data)
        if 'difficulties' in data:
            difficulties = data['difficulties']
            ret['difficulties'] = [
                {'season': diff['season'], 'difficulty': diff['difficulty']}
                for diff in difficulties
            ]
        logger.info("[SubmitDataSerializer][to_internal_value] Успешное преобразование")
        return ret

    def validate(self, data):
        """📌 Валидация данных"""
        logger.info("[SubmitDataSerializer][validate] Валидация данных")
        return data

    def update(self, instance, validated_data):
        """📌 Обновление перевала с сохранением существующих ID записей"""
        logger.info("[SubmitDataSerializer][update] Начало обновления перевала")

        user_data = validated_data.pop("user", None)
        coord_data = validated_data.pop("coord", None)
        difficulties_data = validated_data.pop('difficulties', None)
        images_data = validated_data.pop('images', None)

        # 🔹 Обновление данных пользователя
        if user_data:
            logger.info("[SubmitDataSerializer][update] Обновление данных пользователя")
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # 🔹 Обновление координат
        if coord_data:
            logger.info("[SubmitDataSerializer][update] Обновление координат")
            for attr, value in coord_data.items():
                setattr(instance.coord, attr, value)
            instance.coord.save()

        # 🔹 Обновление остальных полей
        for attr, value in validated_data.items():
            logger.info(f"[SubmitDataSerializer][update] Обновление поля {attr}: {value}")
            setattr(instance, attr, value)
        instance.save()

        # 🔹 Обновление сложностей
        if difficulties_data is not None:
            logger.info("[SubmitDataSerializer][update] Обновление сложностей")
            instance.difficulties.all().delete()
            new_difficulties = []
            for diff in difficulties_data:
                season_id = diff.get('season')
                difficulty_id = diff.get('difficulty')
                try:
                    season = Season.objects.get(id=season_id)
                    difficulty = DifficultyLevel.objects.get(id=difficulty_id)
                    new_difficulties.append(
                        PerevalDifficulty(pereval=instance, season=season, difficulty=difficulty)
                    )
                except (Season.DoesNotExist, DifficultyLevel.DoesNotExist):
                    logger.error(
                        f"[SubmitDataSerializer][update] Ошибка: Неверный ID сезона {season_id} или сложности {difficulty_id}")
                    raise serializers.ValidationError(f"Invalid season ID {season_id} or difficulty ID {difficulty_id}")
            PerevalDifficulty.objects.bulk_create(new_difficulties)
            logger.info("[SubmitDataSerializer][update] Сложности обновлены")

        # 🔹 Обновление изображений
        if images_data is not None:
            logger.info("[SubmitDataSerializer][update] Обновление изображений")
            existing_images = {img.id: img for img in instance.images.all()}
            for img_data in images_data:
                img_id = img_data.get("id")
                delete_flag = img_data.get("delete", False)

                if delete_flag and img_id in existing_images:
                    # 🔹 Удаление записи и файла
                    img = existing_images[img_id]
                    file_path = os.path.join(settings.MEDIA_ROOT, img.data)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"[SubmitDataSerializer][update] Удалён файл: {img.data}")
                    img.delete()
                    logger.info(f"[SubmitDataSerializer][update] Удалена запись изображения ID: {img_id}")
                elif img_id and img_id in existing_images:
                    # 🔹 Обновление существующей записи
                    img = existing_images[img_id]
                    old_data = img.data
                    img.data = img_data.get("data", img.data)
                    img.title = img_data.get("title", img.title)
                    img.save()
                    logger.info(f"[SubmitDataSerializer][update] Обновлена запись изображения ID: {img_id}")
                    # 🔹 Удаление старого файла, если имя изменилось
                    if old_data != img.data:
                        old_file_path = os.path.join(settings.MEDIA_ROOT, old_data)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                            logger.info(f"[SubmitDataSerializer][update] Удалён старый файл: {old_data}")
                else:
                    # 🔹 Создание новой записи
                    PerevalImages.objects.create(pereval=instance, **img_data)
                    logger.info("[SubmitDataSerializer][update] Создана новая запись изображения")

        logger.info("[SubmitDataSerializer][update] Перевал успешно обновлён")
        return instance


class ApiSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор для настройки API"""

    class Meta:
        model = ApiSettings
        fields = ['require_authentication', 'updated_at', 'updated_by']
        read_only_fields = ['updated_at', 'updated_by']  # Эти поля нельзя изменять вручную


# Добавляем новый сериализатор для поиска пользователя по email
class PerevalUserCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerevalUser
        fields = ['id', 'family_name', 'first_name', 'father_name', 'phone', 'email']


class PerevalUserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления данных пользователя (без email)"""

    class Meta:
        model = PerevalUser
        fields = ['family_name', 'first_name', 'father_name', 'phone']
        extra_kwargs = {
            'phone': {'required': False},
            'family_name': {'required': False},
            'first_name': {'required': False},
            'father_name': {'required': False},
        }


class UserConfirmUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения данных пользователя после подтверждения кода"""

    code = serializers.CharField(write_only=True, required=True)  # Код подтверждения (только для записи)

    class Meta:
        model = PerevalUser
        fields = ['family_name', 'first_name', 'father_name', 'phone', 'email', 'code']  # Все изменяемые поля + код

    def validate(self, data):
        """Проверяем код перед изменением"""
        user = self.instance  # Получаем пользователя
        input_code = data.pop("code", None)

        if not input_code:
            raise serializers.ValidationError({"code": "Код подтверждения обязателен."})

        if user.confirmation_code != input_code:  # Проверяем код
            raise serializers.ValidationError({"code": "Неверный код подтверждения."})

        return data  # Возвращаем обновленные данные


class PerevalAddedSerializer(serializers.ModelSerializer):
    """Сериализатор для модели PerevalAdded"""

    class Meta:
        model = PerevalAdded
        fields = '__all__'  # Или указать конкретные поля