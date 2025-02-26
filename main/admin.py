# /Mountain Pass Application/main/admin.py

from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from main.models import (
    ApiSettings, ModeratorGroup, DifficultyLevel, Season, Coords,
    PerevalAdded, PerevalImages, WeatherInfo, PerevalDifficulty, PerevalStatus, PerevalUser
)

@admin.register(ApiSettings)
class ApiSettingsAdmin(admin.ModelAdmin):
    list_display = ('require_authentication', 'updated_at', 'updated_by')
    readonly_fields = ('updated_at', 'updated_by')

@admin.register(ModeratorGroup)
class ModeratorGroupAdmin(admin.ModelAdmin):
    list_display = ('user', 'added_by')
    search_fields = ('user__email',)

@admin.register(PerevalAdded)
class PerevalAddedAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PerevalAdded._meta.fields]

admin.site.register(DifficultyLevel)
admin.site.register(Season)
admin.site.register(Coords)
admin.site.register(PerevalImages)
admin.site.register(WeatherInfo)
admin.site.register(PerevalDifficulty)
admin.site.register(PerevalStatus)
admin.site.register(PerevalUser)
admin.site.register(Group)  # Добавляем группы пользователей
admin.site.register(Permission)  # Добавляем права пользователей
