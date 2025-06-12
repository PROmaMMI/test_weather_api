from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ForecastOverride
from .serializers import (
    CurrentWeatherSerializer, 
    ForecastSerializer,
    ForecastInputSerializer
)
from .services import (
    WeatherService, 
    CityNotFoundError, 
    ExternalAPIError,
    ForecastNotFoundError
)
from datetime import datetime
from django.utils import timezone

class CurrentWeatherView(APIView):
    def get(self, request):
        city = request.query_params.get('city')
        if not city:
            return Response(
                {"error": "Parameter 'city' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            weather_data = WeatherService.get_current_weather(city)
            serializer = CurrentWeatherSerializer(weather_data)
            return Response(serializer.data)
        except CityNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ExternalAPIError as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ForecastView(APIView):
    def get(self, request):
        city = request.query_params.get('city')
        date_str = request.query_params.get('date')
        
        if not city or not date_str:
            return Response(
                {"error": "Parameters 'city' and 'date' are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Преобразование даты
        try:
            forecast_date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use dd.MM.yyyy"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация даты
        today = timezone.now().date()
        if forecast_date < today:
            return Response(
                {"error": "Date cannot be in the past"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if (forecast_date - today).days > 3:
            return Response(
                {"error": "Forecast is available only for next 3 days"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка переопределенных данных
        try:
            override = ForecastOverride.objects.get(city=city, date=forecast_date)
            return Response({
                "min_temperature": override.min_temperature,
                "max_temperature": override.max_temperature
            })
        except ForecastOverride.DoesNotExist:
            pass
        
        # Получение реального прогноза
        try:
            forecast_data = WeatherService.get_forecast(city, forecast_date)
            return Response(forecast_data)
        except CityNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ForecastNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ExternalAPIError as e:
            return Response({"error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        serializer = ForecastInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        city = validated_data['city']
        forecast_date = validated_data['date']
        min_temp = validated_data['min_temperature']
        max_temp = validated_data['max_temperature']
        
        # Создание или обновление записи
        obj, created = ForecastOverride.objects.update_or_create(
            city=city,
            date=forecast_date,
            defaults={
                'min_temperature': min_temp,
                'max_temperature': max_temp
            }
        )
        
        return Response({
            "city": city,
            "date": forecast_date.strftime("%d.%m.%Y"),
            "min_temperature": min_temp,
            "max_temperature": max_temp
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)