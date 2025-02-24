#  /Mountain Pass Application/main/admin.py


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from main.models import (
    ApiSettings, UserProfile, ModeratorGroup,
    DifficultyLevel, Season, Coords,
    PerevalAdded, PerevalImages, WeatherInfo, PerevalDifficulty
)
import tempfile
import os
from django.http import HttpResponse
from django.core.management import call_command
from django.urls import path

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

class UserProfileInline(admin.StackedInline):
    """Добавляем `phone` и `middle_name` в `UserAdmin`"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Дополнительные данные"

class CustomUserAdmin(UserAdmin):
    """Расширенный `UserAdmin` с `phone` и `middle_name`"""
    inlines = (UserProfileInline,)

admin.site.register(User, CustomUserAdmin)  # ✅ Регистрируем `User`


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


# -----------------------------------------------------
# Добавление ER-диаграммы моделей
# -----------------------------------------------------
#
# def er_diagram_view(request):
#     """
#     Генерирует ER-диаграмму для всех моделей и возвращает её как изображение.
#     Для работы требуется установка django-extensions и pygraphviz.
#     """
#     with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
#         tmp_file_path = tmp.name
#     try:
#         call_command("graph_models", "-a", "-o", tmp_file_path)
#         with open(tmp_file_path, "rb") as f:
#             image_data = f.read()
#         return HttpResponse(image_data, content_type="image/png")
#     finally:
#         if os.path.exists(tmp_file_path):
#             os.remove(tmp_file_path)
#
# # Переопределяем urls админки для добавления нового эндпоинта
# original_get_urls = admin.site.get_urls()
# def get_urls():
#     my_urls = [
#         path('er-diagram/', admin.site.admin_view(er_diagram_view), name="er-diagram"),
#     ]
#     return my_urls + original_get_urls
# admin.site.get_urls = get_urls