from django.contrib import admin
from main.models import ApiSettings  # Импортируем модель


@admin.register(ApiSettings)
class ApiSettingsAdmin(admin.ModelAdmin):
    """Добавляем настройку API в админку"""
    list_display = ('require_authentication', 'updated_at', 'updated_by')  # Поля в списке
    readonly_fields = ('updated_at', 'updated_by')  # Эти поля нельзя редактировать вручную
