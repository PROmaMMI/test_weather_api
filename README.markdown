# Weather API

## Описание

Это Django REST API для получения текущей погоды и прогноза погоды. API использует внешний сервис [WeatherAPI](https://www.weatherapi.com/) для получения данных о погоде и предоставляет конечные точки для доступа к текущей погоде и прогнозу на ближайшие 3 дня для указанного города(меньше 10 дней, потому что тарифный план больше не позволяет, логика от количества дней не меняется). Также реализована возможность переопределения прогноза погоды путем сохранения пользовательских данных в базе данных.

## Возможности

- Получение текущей погоды для указанного города.
- Получение прогноза погоды на конкретную дату (в пределах 3 дней).
- Создание или обновление пользовательского прогноза погоды.

## Требования

- Python 3.6+
- Django 4.2.7
- Django REST Framework 3.14.0
- requests 2.31.0
- python-dotenv 1.0.0
- pytest >=8.2,<9
- pytest-django 4.5.2

## Установка

1. Клонируйте репозиторий:

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

3. Настройте переменные окружения:

   - Скопируйте файл `.env.template` в `.env`:

     ```bash
     cp .env.template .env
     ```

   - Отредактируйте файл `.env` и добавьте ваш API-ключ от [WeatherAPI](https://www.weatherapi.com/).

4. Примените миграции Django:

   ```bash
   python manage.py migrate
   ```

## Запуск приложения

Запустите сервер разработки Django:

```bash
python manage.py runserver
```

API будет доступен по адресу `http://localhost:8000`.

## Конечные точки API

| Конечная точка | Метод | Описание | Параметры |
|----------------|-------|----------|-----------|
| `/api/weather/current` | GET | Получение текущей погоды для города | `city` (обязательный) |
| `/api/weather/forecast` | GET | Получение прогноза погоды на указанную дату | `city` (обязательный), `date` (формат: `dd.MM.yyyy`) |
| `/api/weather/forecast` | POST | Создание или обновление пользовательского прогноза погоды | JSON: `city`, `date` (формат: `dd.MM.yyyy`), `min_temperature`, `max_temperature` |

### Примеры запросов

1. **Получение текущей погоды**:

   ```bash
   curl http://localhost:8000/api/weather/current?city=Moscow
   ```

2. **Получение прогноза погоды**:

   ```bash
   curl http://localhost:8000/api/weather/forecast?city=Moscow&date=12.06.2025
   ```

3. **Переопределение прогноза погоды**:

   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"city": "Moscow", "date": "12.06.2025", "min_temperature": 10, "max_temperature": 20}' http://localhost:8000/api/weather/forecast
   ```
## Переменные окружения

В файле `.env` необходимо указать следующие переменные:

- `WEATHER_API_KEY`: Ваш API-ключ от [WeatherAPI](https://www.weatherapi.com/).

- `WEATHER_API_URL`: Ссылка не меняется

- `SECRET_KEY`: Секретный ключ из settings.py Django

Пример файла `.env`:

```env
WEATHER_API_KEY=your_api_key_here

WEATHER_API_URL=https://api.weatherapi.com/v1

SECRET_KEY=your_secret_django_key_here
```
