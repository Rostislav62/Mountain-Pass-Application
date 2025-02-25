#  /Mountain Pass Application/main/admin.py


from django.contrib import admin
from django.contrib.auth.models import User
from main.models import (
    ApiSettings, ModeratorGroup,
    DifficultyLevel, Season, Coords,
    PerevalAdded, PerevalImages, WeatherInfo, PerevalDifficulty
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


# ✅ Проверяем, зарегистрирован ли `User`, перед тем как регистрировать
if admin.site.is_registered(User):
    admin.site.unregister(User)  # ❌ Удаляем стандартную регистрацию


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
    list_display = ('title', 'user', 'status', 'add_time')
    inlines = [PerevalImagesInline, PerevalDifficultyInline, WeatherInfoInline]


admin.site.register(PerevalAdded, PerevalAddedAdmin)

# Регистрируем остальные модели для отображения в админке

admin.site.register(DifficultyLevel)
admin.site.register(Season)
admin.site.register(Coords)
admin.site.register(PerevalImages)
admin.site.register(WeatherInfo)
admin.site.register(PerevalDifficulty)
