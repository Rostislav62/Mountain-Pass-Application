#  /Mountain Pass Application/main/services/openweather.py

import os
import requests


def get_weather_forecast(latitude, longitude):
    """Запрашивает прогноз погоды через OpenWeather API"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OpenWeather API Key не найден"}

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric&lang=ru"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"]
        }
    return {"error": "Ошибка при запросе погоды"}
