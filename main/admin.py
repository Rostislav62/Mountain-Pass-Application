# /Mountain Pass Application/main/admin.py

# Импортируем модуль admin из Django для работы с админкой
from django.contrib import admin
# Импортируем UserAdmin для кастомизации админки пользователей Django
from django.contrib.auth.admin import UserAdmin
# Импортируем модель User из Django для управления пользователями
from django.contrib.auth.models import User
# Импортируем все модели из main.models для регистрации в админке
from main.models import (
    ApiSettings, ModeratorGroup, DifficultyLevel, Season, Coords,
    PerevalAdded, PerevalImages, PerevalDifficulty,
    PerevalStatus, PerevalUser
)

# Регистрируем модель ApiSettings с кастомной настройкой админки
@admin.register(ApiSettings)
class ApiSettingsAdmin(admin.ModelAdmin):
    """Класс для управления настройками API в админке"""
    # Отображаем поля: флаг аутентификации, дата обновления, кто обновил
    list_display = ('id', 'require_authentication', 'updated_at', 'updated_by')
    # Делаем поля updated_at и updated_by только для чтения
    readonly_fields = ('updated_at', 'updated_by')
    # Добавляем поиск по require_authentication для удобства
    search_fields = ('require_authentication',)

# Регистрируем модель ModeratorGroup с кастомной настройкой админки
@admin.register(ModeratorGroup)
class ModeratorGroupAdmin(admin.ModelAdmin):
    """Класс для управления группами модераторов в админке"""
    # Отображаем все поля: ID, пользователь, кто добавил
    list_display = ('id', 'user', 'added_by')
    # Добавляем поиск по email пользователя
    search_fields = ('user__email',)

# Регистрируем модель PerevalStatus с кастомной настройкой админки
@admin.register(PerevalStatus)
class PerevalStatusAdmin(admin.ModelAdmin):
    """Класс для управления статусами перевалов в админке"""
    # Отображаем все поля: ID и имя статуса
    list_display = ('id', 'name')
    # Сортируем по ID для удобства
    ordering = ('id',)
    # Добавляем поиск по имени статуса
    search_fields = ('name',)

# Регистрируем модель PerevalUser с кастомной настройкой админки
@admin.register(PerevalUser)
class PerevalUserAdmin(admin.ModelAdmin):
    """Класс для управления пользователями перевалов в админке"""
    # Отображаем все поля: ID, фамилия, имя, email, телефон
    list_display = ('id', 'family_name', 'first_name', 'father_name', 'email', 'phone')
    # Добавляем поиск по email, фамилии и имени
    search_fields = ('email', 'family_name', 'first_name')
    # Добавляем фильтр по email для удобства
    list_filter = ('email',)

# Проверяем, зарегистрирован ли User, чтобы избежать конфликтов
if admin.site.is_registered(User):
    # Если User уже зарегистрирован, убираем стандартную регистрацию
    admin.site.unregister(User)

# Регистрируем модель User с кастомной настройкой админки
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Класс для расширенного управления пользователями Django в админке"""
    # Отображаем все ключевые поля: имя пользователя, email, флаги прав, активность
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login')
    # Добавляем поиск по email и имени пользователя
    search_fields = ('email', 'username')
    # Добавляем фильтры по правам и активности
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    # Определяем структуру формы редактирования
    fieldsets = (
        (None, {'fields': ('username', 'password')}),  # Базовые поля логина
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),  # Личные данные
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  # Права
        ('Дополнительно', {'fields': ('last_login', 'date_joined')}),  # Даты
    )
    # Добавляем горизонтальные фильтры для групп и разрешений
    filter_horizontal = ('groups', 'user_permissions')

# Регистрируем модель DifficultyLevel с кастомной настройкой админки
@admin.register(DifficultyLevel)
class DifficultyLevelAdmin(admin.ModelAdmin):
    """Класс для управления уровнями сложности в админке"""
    # Отображаем все поля: код, описание, характеристики, требования
    list_display = ('id', 'code', 'description', 'characteristics', 'requirements')
    # Добавляем поиск по коду и описанию
    search_fields = ('code', 'description')
    # Добавляем фильтр по коду
    list_filter = ('code',)

# Регистрируем модель Season с кастомной настройкой админки
@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    """Класс для управления сезонами в админке"""
    # Отображаем все поля: ID, код, название
    list_display = ('id', 'code', 'name')
    # Добавляем поиск по названию
    search_fields = ('name',)
    # Добавляем фильтр по коду
    list_filter = ('code',)

# Регистрируем модель Coords с кастомной настройкой админки
@admin.register(Coords)
class CoordsAdmin(admin.ModelAdmin):
    """Класс для управления координатами в админке"""
    # Отображаем все поля: ID, широта, долгота, высота
    list_display = ('id', 'latitude', 'longitude', 'height')
    # Добавляем поиск по широте и долготе
    search_fields = ('latitude', 'longitude')
    # Добавляем фильтр по высоте
    list_filter = ('height',)

# Регистрируем модель PerevalImages с кастомной настройкой админки
@admin.register(PerevalImages)
class PerevalImagesAdmin(admin.ModelAdmin):
    """Класс для управления изображениями перевалов в админке"""
    # Отображаем все поля: ID, перевал, данные изображения, название
    list_display = ('id', 'pereval', 'data', 'title')
    # Добавляем поиск по названию изображения
    search_fields = ('title',)
    # Добавляем фильтр по перевалу
    list_filter = ('pereval',)


# Регистрируем модель PerevalDifficulty с кастомной настройкой админки
@admin.register(PerevalDifficulty)
class PerevalDifficultyAdmin(admin.ModelAdmin):
    """Класс для управления сложностями перевалов в админке"""
    # Отображаем все поля: ID, перевал, сезон, уровень сложности
    list_display = ('id', 'pereval', 'season', 'difficulty')
    # Добавляем поиск по перевалу и сезону
    search_fields = ('pereval__title', 'season__name')
    # Добавляем фильтр по сезону и сложности
    list_filter = ('season', 'difficulty')

# Определяем inline-класс для изображений перевалов
class PerevalImagesInline(admin.TabularInline):
    # Связываем с моделью PerevalImages
    model = PerevalImages
    # Устанавливаем 0 дополнительных пустых форм по умолчанию
    extra = 0

# Определяем inline-класс для сложностей перевалов
class PerevalDifficultyInline(admin.TabularInline):
    # Связываем с моделью PerevalDifficulty
    model = PerevalDifficulty
    # Устанавливаем 0 дополнительных пустых форм по умолчанию
    extra = 0


# Регистрируем модель PerevalAdded с кастомной настройкой админки
@admin.register(PerevalAdded)
class PerevalAddedAdmin(admin.ModelAdmin):
    """Класс для управления перевалами в админке"""
    # Отображаем все поля модели PerevalAdded
    list_display = [field.name for field in PerevalAdded._meta.fields]
    # Добавляем поиск по ID, названию и email пользователя
    search_fields = ('id', 'title', 'user__email')
    # Добавляем фильтры по статусу и времени добавления
    list_filter = ('status', 'add_time')
    # Подключаем inline-таблицы для связанных данных
    inlines = [PerevalImagesInline, PerevalDifficultyInline]