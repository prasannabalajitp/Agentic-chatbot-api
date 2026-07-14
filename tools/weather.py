from langchain.tools import tool
from service.weather_service import WeatherService

weather_service = WeatherService()

@tool(parse_docstring=True)
def get_weather(city: str) -> dict:
    """
    Get the current weather of the city.

    Args:
        city: City to get the weather.

    Returns:
        The weather details in a dictionary.
    """
    return weather_service.get_weather(city=city)
