from django.core.management.base import BaseCommand
from main.models import DifficultyLevel, Season


class Command(BaseCommand):
    help = "Заполняет таблицы DifficultyLevel и Season начальными значениями"

    def handle(self, *args, **kwargs):
        difficulty_data = [
            {"code": "1A", "description": "Лёгкий перевал, доступный для пешеходных туристов. Минимальный уклон."},
            {"code": "1B", "description": "Небольшой снежный/скальный участок, возможны тросовые перила."},
            {"code": "2A", "description": "Средняя сложность. Крутые скальные участки, возможен лёд."},
            {"code": "2B", "description": "Сложные скалы, ледники, требуется специальное снаряжение."},
            {"code": "3A", "description": "Высокая сложность. Сильный наклон, ледники, возможны трещины."},
            {"code": "3B", "description": "Максимально сложные перевалы. Требуется высокая квалификация."}
        ]

        season_data = [
            {"code": "winter", "name": "Зима"},
            {"code": "summer", "name": "Лето"},
            {"code": "autumn", "name": "Осень"},
            {"code": "spring", "name": "Весна"}
        ]

        # Добавляем данные в БД
        for diff in difficulty_data:
            DifficultyLevel.objects.get_or_create(**diff)

        for season in season_data:
            Season.objects.get_or_create(**season)

        self.stdout.write(self.style.SUCCESS("Таблицы DifficultyLevel и Season успешно заполнены"))
