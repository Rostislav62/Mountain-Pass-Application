#  /Mountain Pass Application/main/services/strava.py

import os
import requests

def get_strava_track(activity_id):
    """Получает данные о треке Strava"""
    api_key = os.getenv("STRAVA_API_KEY")
    if not api_key:
        return {"error": "Strava API Key не найден"}

    url = f"https://www.strava.com/api/v3/activities/{activity_id}?access_token={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    return {"error": "Ошибка при получении трека Strava"}
