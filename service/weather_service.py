from core.config import settings
from core.constants import constants
import requests

class WeatherService:
    
    def __init__(self):
        pass

    def get_weather(self, city: str) -> str:
        try:
            geo_response = requests.get(
                settings.GEO_URL,
                params={constants.NAME: city},
                timeout=10
            )
            geo_response.raise_for_status()

            geo_data = geo_response.json()

            if not geo_data.get(constants.RESULTS):
                return {"error": f"City '{city}' not found."}

            location = geo_data[constants.RESULTS][0]

            weather_response = requests.get(
                settings.WEATHER_URL,
                params={
                    constants.LATITUDE: location[constants.LATITUDE],
                    constants.LONGITUDE: location[constants.LONGITUDE],
                    constants.CURRENT: constants.TEMP_VALUES,
                    constants.TIMEZONE: constants.AUTO
                },
                timeout=10
            )
            weather_response.raise_for_status()

            current = weather_response.json()[constants.CURRENT]
            rain = "Yes" if current["rain"] > 0 else "No"

            return (
                f"Weather in {location['name']}, {location['country']}\n"
                f"Temperature: {current['temperature_2m']}°C\n"
                f"Feels Like: {current['apparent_temperature']}°C\n"
                f"Humidity: {current['relative_humidity_2m']}%\n"
                f"Wind Speed: {current['wind_speed_10m']} km/h\n"
                f"Rain: {rain}"
            )
        
        except requests.RequestException as ex:
            return f"Unable to fetch weather details. {str(ex)}"
