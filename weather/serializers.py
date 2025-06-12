from rest_framework import serializers
from .models import ForecastOverride
from datetime import date, timedelta, datetime
import re

class CurrentWeatherSerializer(serializers.Serializer):
    temperature = serializers.FloatField()
    local_time = serializers.CharField()

class ForecastSerializer(serializers.Serializer):
    min_temperature = serializers.FloatField()
    max_temperature = serializers.FloatField()

class ForecastInputSerializer(serializers.Serializer):
    city = serializers.CharField(max_length=100, required=True)
    date = serializers.CharField(required=True)
    min_temperature = serializers.FloatField(required=True)
    max_temperature = serializers.FloatField(required=True)
    
    def validate_date(self, value):
        # Проверка формата даты
        if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', value):
            raise serializers.ValidationError("Неверный формат даты. Используйте dd.MM.yyyy")
        
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise serializers.ValidationError("Неверная дата")
        
        today = date.today()
        if parsed_date < today:
            raise serializers.ValidationError("Дата не может быть в прошлом")
        
        if (parsed_date - today).days > 3:
            raise serializers.ValidationError("Прогноз доступен только на 3 дней вперед")
        
        return parsed_date
    
    def validate(self, data):
        if 'min_temperature' in data and 'max_temperature' in data:
            if data['min_temperature'] > data['max_temperature']:
                raise serializers.ValidationError("Минимальная температура не может превышать максимальную")
        return data