from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from main.models import ApiSettings, UserProfile, ModeratorGroup

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
