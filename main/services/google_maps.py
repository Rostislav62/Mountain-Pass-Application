#  /Mountain Pass Application/main/services/google_maps.py

import os


def get_google_map_link(latitude, longitude):
    """Генерирует ссылку на Google Maps с координатами перевала"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return "Google Maps API Key не найден"

    return f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}&key={api_key}"
