from django.urls import path
from .views import CurrentWeatherView, ForecastView

urlpatterns = [
    path('current', CurrentWeatherView.as_view(), name='current-weather'),
    path('forecast', ForecastView.as_view(), name='weather-forecast'),
]