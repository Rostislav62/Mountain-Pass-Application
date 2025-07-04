#  /Mountain Pass Application/main/models.py

from django.db import models
from django.contrib.auth.models import User


class ModeratorGroup(models.Model):
    """Группа модераторов"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="moderator_group")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="added_moderators")

    def __str__(self):
        return f"Модератор: {self.user.email} (Добавлен {self.added_by.email})"


class DifficultyLevel(models.Model):
    """Описание сложности перевала"""
    code = models.CharField(max_length=2, unique=True)  # Например, '1A', '3B'
    description = models.CharField(max_length=255)  # Полное описание сложности
    characteristics = models.TextField(blank=True, null=True)  # Характеристики (например, "Пологие склоны, высота до 3000 м")
    requirements = models.TextField(blank=True, null=True)  # Требования к снаряжению и навыкам (например, "Базовые навыки, треккинговые палки")

    def __str__(self):
        return self.description


class Season(models.Model):
    """Сезоны для перевалов"""
    code = models.CharField(max_length=10, unique=True)  # Например, 'winter'
    name = models.CharField(max_length=20, unique=True)  # Полное название (Зима, Лето)

    def __str__(self):
        return self.name


class Coords(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    height = models.IntegerField()

    def __str__(self):
        return f"({self.latitude}, {self.longitude}, {self.height})"


class PerevalStatus(models.Model):
    """Таблица статусов перевалов"""

    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class PerevalUser(models.Model):
    """Модель для хранения информации о пользователях, вносящих данные о перевалах"""

    family_name = models.CharField(max_length=255)  # Фамилия
    first_name = models.CharField(max_length=255)  # Имя
    father_name = models.CharField(max_length=255, blank=True, null=True, default="")  # Отчество (может быть пустым)
    phone = models.CharField(max_length=20, unique=False, blank=False, null=False)  # Телефон (уникальный)
    email = models.EmailField(unique=False, blank=False, null=False)  # Email (уникальный)
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания (автоматическая)

    def __str__(self):
        return f"{self.family_name} {self.first_name} ({self.email})"


    class Meta:
        verbose_name = "Пользователь перевалов"
        verbose_name_plural = "Пользователи перевалов"


class PerevalAdded(models.Model):
    """Модель для хранения перевалов"""

    user = models.ForeignKey(
        PerevalUser,
        on_delete=models.SET_DEFAULT,
        default=1  # Фиксированный admin_user (ID=1)
    )
    coord = models.ForeignKey(Coords, on_delete=models.CASCADE)
    beautyTitle = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    other_titles = models.CharField(max_length=255, blank=True, null=True)
    connect = models.BooleanField(default=False)  # Перевал отправлен на сервер (True) или нет (False)
    add_time = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(PerevalStatus, on_delete=models.CASCADE, default=1)  # Привязываем к PerevalStatus
    route_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class PerevalImages(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE, related_name="images")
    data = models.CharField(max_length=255, default="")  # Ссылка на изображение или бинарные данные
    title = models.CharField(max_length=255, default="")  # Описание изображения

    def __str__(self):
        return f"{self.title} ({self.data})"


class PerevalDifficulty(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE, related_name="difficulties")
    season = models.ForeignKey(Season, on_delete=models.CASCADE)  # 🔥 Теперь сезон — внешний ключ
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE, null=True,
                                   default=None)  # 🔥 Теперь сложность — внешний ключ

    class Meta:
        unique_together = ('pereval', 'season') # Запрещаем дублирование данных для одного сезона

    def __str__(self):
        return f"{self.pereval.title} - {self.season.name}: {self.difficulty or 'No difficulty'}"


class ApiSettings(models.Model):
    """Настройки API: управляет требованием авторизации"""

    require_authentication = models.BooleanField(default=False)  # 🔥 По умолчанию API открыт
    updated_at = models.DateTimeField(auto_now=True)  # Время последнего изменения
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кто изменил"
    )  # Админ, который изменил настройку

    def __str__(self):
        return f"API Auth Required: {self.require_authentication}"


class EmailConfirmationToken(models.Model):
    """Модель для хранения кода подтверждения email"""
    user = models.OneToOneField(PerevalUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Код для {self.user.email}: {self.code}"