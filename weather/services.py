import requests
import os
from django.conf import settings
from datetime import datetime
from rest_framework.exceptions import APIException

class WeatherService:
    API_BASE_URL = "http://api.weatherapi.com/v1"
    
    @staticmethod
    def _make_request(endpoint, params):
        """Базовый метод для выполнения запросов к API"""
        try:
            url = f"{WeatherService.API_BASE_URL}{endpoint}"
            api_key = settings.WEATHER_API_KEY
            
            response = requests.get(
                url,
                params={"key": api_key, **params},
                timeout=5
            )
            
            # Успешный запрос
            if response.status_code == 200:
                return response.json()
                
            # Обработка ошибок API
            error_data = response.json().get("error", {})
            error_code = error_data.get("code")
            error_message = error_data.get("message", "Unknown error")
            
            # Специфичные ошибки
            if error_code == 1006:  # Location not found
                raise CityNotFoundError(f"City '{params.get('q')}' not found")
            elif error_code == 2008:  # API rate limit exceeded
                raise ExternalAPIError("API rate limit exceeded")
            else:
                raise ExternalAPIError(f"API error {error_code}: {error_message}")
                
        except requests.exceptions.RequestException as e:
            raise ExternalAPIError(f"Network error: {str(e)}")

    @staticmethod
    def get_current_weather(city):
        """Получение текущей погоды для города"""
        data = WeatherService._make_request(
            "/current.json", 
            {"q": city}
        )
        
        # Извлекаем и форматируем время
        local_time = data["location"]["localtime"]
        time_parts = local_time.split(" ")
        time_str = time_parts[1][:5] if len(time_parts) > 1 else "00:00"
        
        return {
            "temperature": data["current"]["temp_c"],
            "local_time": time_str
        }

    @staticmethod
    def get_forecast(city, target_date):
        """Получение прогноза погоды для города на конкретную дату (3 дня)"""
        data = WeatherService._make_request(
            "/forecast.json", 
            {"q": city, "days": 3}
        )
        
        # Ищем нужную дату в прогнозе
        target_date_str = target_date.strftime("%Y-%m-%d")
        for day in data["forecast"]["forecastday"]:
            if day["date"] == target_date_str:
                return {
                    "min_temperature": day["day"]["mintemp_c"],
                    "max_temperature": day["day"]["maxtemp_c"]
                }
        
        # Если дата не найдена (выходит за 3 дня)
        raise ForecastNotFoundError(
            f"No forecast for {target_date_str}. Max forecast period is 3 days."
        )

# Кастомные исключения
class CityNotFoundError(APIException):
    status_code = 404
    default_detail = 'City not found'
    default_code = 'city_not_found'

class ExternalAPIError(APIException):
    status_code = 503
    default_detail = 'Weather service unavailable'
    default_code = 'external_service_error'

class ForecastNotFoundError(APIException):
    status_code = 400
    default_detail = 'Forecast not available for this date'
    default_code = 'forecast_not_found'