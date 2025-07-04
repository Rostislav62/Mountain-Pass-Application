#  /Mountain Pass Application/main/services/yandex_maps.py

import os

def get_yandex_route(latitude, longitude):
    """Генерирует ссылку на маршрут в Яндекс.Навигаторе"""
    api_key = os.getenv("YANDEX_MAPS_API_KEY")
    if not api_key:
        return "Yandex Maps API Key не найден"

    return f"https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
