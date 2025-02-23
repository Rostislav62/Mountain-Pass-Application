#  /Mountain Pass Application/main/models.py

from django.db import models
from django.contrib.auth.models import User
# # Импортируем Season и DifficultyLevel перед их использованием
# from main.models import Season, DifficultyLevel


class UserProfile(models.Model):
    """Дополнительные данные для пользователей"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Телефон")

    def __str__(self):
        return f"{self.user.username} (Профиль)"


class ModeratorGroup(models.Model):
    """Группа модераторов"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="moderator_group")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="added_moderators")

    def __str__(self):
        return f"Модератор: {self.user.email} (Добавлен {self.added_by.email})"


class DifficultyLevel(models.Model):
    """Описание сложности перевала"""
    code = models.CharField(max_length=2, unique=True)  # Например, '1A', '3B'
    description = models.TextField(unique=True)  # Полное описание сложности

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


class PerevalAdded(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coord = models.ForeignKey(Coords, on_delete=models.CASCADE)
    beautyTitle = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    other_titles = models.CharField(max_length=255, blank=True, null=True)
    connect = models.TextField(blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    route_description = models.TextField(blank=True, null=True)
    hazards = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class PerevalImages(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE, related_name="images")
    data = models.TextField(default="")  # Ссылка на изображение или бинарные данные
    title = models.CharField(max_length=255, default="")  # Описание изображения

    def __str__(self):
        return f"{self.title} ({self.data})"


# class PerevalGpsTracks(models.Model):
#     pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
#     track_path = models.TextField()
#
#     def __str__(self):
#         return self.track_path


# class PerevalHistory(models.Model):
#     pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     pass_date = models.DateField()
#     comments = models.TextField(blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.pereval.title} - {self.pass_date}"


# class RelatedObjects(models.Model):
#     RELATED_TYPE_CHOICES = [
#         ('mountain', 'Mountain'),
#         ('ridge', 'Ridge'),
#         ('other', 'Other'),
#     ]
#
#     pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
#     related_name = models.CharField(max_length=255)
#     related_type = models.CharField(max_length=50, choices=RELATED_TYPE_CHOICES)
#
#     def __str__(self):
#         return f"{self.related_name} ({self.related_type})"


class WeatherInfo(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    precipitation = models.CharField(max_length=50, blank=True, null=True)
    weather_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Weather for {self.pereval.title} on {self.weather_date}"


class PerevalDifficulty(models.Model):
    """Связь перевалов с уровнем сложности и сезоном"""
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE, related_name="difficulties")
    season = models.ForeignKey(Season, on_delete=models.CASCADE)  # 🔥 Теперь сезон — внешний ключ
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE, null=True, default=None)  # 🔥 Теперь сложность — внешний ключ

    class Meta:
        unique_together = ('pereval', 'season')  # Запрещаем дублирование данных для одного сезона

    def __str__(self):
        return f"{self.pereval.title}: {self.season.name} - {self.difficulty.description}"


class ApiSettings(models.Model):
    """Настройки API: управляет требованием авторизации"""

    require_authentication = models.BooleanField(default=False)  # 🔥 По умолчанию API открыт
    updated_at = models.DateTimeField(auto_now=True)  # Время последнего изменения
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Кто изменил"
    )  # Админ, который изменил настройку

    def __str__(self):
        return f"API Auth Required: {self.require_authentication}"
