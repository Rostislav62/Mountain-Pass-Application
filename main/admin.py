# /Mountain Pass Application/main/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from main.models import (
    ApiSettings, ModeratorGroup,
    DifficultyLevel, Season, Coords,
    PerevalAdded, PerevalImages, WeatherInfo, PerevalDifficulty,
    PerevalStatus, PerevalUser
)

@admin.register(ApiSettings)
class ApiSettingsAdmin(admin.ModelAdmin):
    """Добавляем настройку API в админку"""
    list_display = ('require_authentication', 'updated_at', 'updated_by')
    readonly_fields = ('updated_at', 'updated_by')

@admin.register(ModeratorGroup)
class ModeratorGroupAdmin(admin.ModelAdmin):
    """Управление модераторами"""
    list_display = ('user', 'added_by')
    search_fields = ('user__email',)

@admin.register(PerevalStatus)
class PerevalStatusAdmin(admin.ModelAdmin):
    """Администрирование статусов перевалов"""
    list_display = ('id', 'name')
    ordering = ('id',)

@admin.register(PerevalUser)
class PerevalUserAdmin(admin.ModelAdmin):
    """Администрирование пользователей перевалов"""
    list_display = ('id', 'family_name', 'first_name', 'email', 'phone')
    search_fields = ('email', 'family_name', 'first_name')

# ✅ Проверяем, зарегистрирован ли `User`, перед тем как регистрировать
if admin.site.is_registered(User):
    admin.site.unregister(User)  # ❌ Удаляем стандартную регистрацию

# ✅ Повторно регистрируем с привязкой к `ModeratorGroup`
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Расширяем админку пользователей Django"""
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Дополнительно', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions')

admin.site.register(DifficultyLevel)
admin.site.register(Season)
admin.site.register(Coords)
admin.site.register(PerevalImages)
admin.site.register(WeatherInfo)
admin.site.register(PerevalDifficulty)

# Inlines для модели PerevalAdded
class PerevalImagesInline(admin.TabularInline):
    model = PerevalImages
    extra = 0

class PerevalDifficultyInline(admin.TabularInline):
    model = PerevalDifficulty
    extra = 0

class WeatherInfoInline(admin.TabularInline):
    model = WeatherInfo
    extra = 0


class PerevalAddedAdmin(admin.ModelAdmin):
    """Отображение всех полей модели PerevalAdded в админке"""

    list_display = [field.name for field in PerevalAdded._meta.fields]  # ✅ Вывести ВСЕ поля

    # Позволяет искать по title, id и email пользователя
    search_fields = ('id', 'title', 'user__email')

    # Фильтрация по статусу
    list_filter = ('status', 'add_time')


admin.site.register(PerevalAdded, PerevalAddedAdmin)
