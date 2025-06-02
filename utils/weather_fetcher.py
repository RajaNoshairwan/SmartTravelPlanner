"""
Weather fetcher module for travel planning.

This module provides functions to fetch real-time weather information
using the OpenWeatherMap API.
"""

import requests
import os
from datetime import datetime
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
API_KEY = os.getenv("OPENWEATHER_API_KEY", "ad9dd2f3e0d38465e08d5b29708471bc")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
UNITS = "metric"  # Use metric units (Celsius)

def get_weather_info(city: str) -> Optional[Dict]:
    """
    Get current weather information for a city using OpenWeatherMap API.
    
    Args:
        city (str): Name of the city
        
    Returns:
        Optional[Dict]: Dictionary containing weather information or None if error
    """
    try:
        # Check if API key is set
        if not API_KEY:
            logger.error("OpenWeather API key not found")
            return None
        
        # Get city coordinates first
        from utils.distance_calculator import get_coordinates
        try:
            lat, lon = get_coordinates(city)
        except Exception as e:
            logger.error(f"Could not get coordinates for {city}: {e}")
            return None
        
        # Prepare request parameters using coordinates instead of city name
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": UNITS
        }
        
        # Make API request
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse response
        data = response.json()
        
        # Extract relevant information
        weather_info = {
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"], 1),
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "last_updated": datetime.fromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"Successfully fetched weather for {city} at coordinates {lat}, {lon}")
        return weather_info
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather for {city}: {e}")
        return None
    except (KeyError, ValueError) as e:
        logger.error(f"Error parsing weather data for {city}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting weather for {city}: {e}")
        return None

def get_weather_icon_url(icon_code: str) -> str:
    """
    Get the URL for a weather icon.
    
    Args:
        icon_code (str): OpenWeatherMap icon code
        
    Returns:
        str: URL for the weather icon
    """
    return f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

def get_weather_advice(weather_info: Dict) -> str:
    """
    Get travel advice based on weather conditions.
    
    Args:
        weather_info (Dict): Weather information dictionary
        
    Returns:
        str: Weather-based travel advice
    """
    try:
        temp = weather_info["temperature"]
        description = weather_info["description"].lower()
        wind_speed = weather_info["wind_speed"]
        
        advice = []
        
        # Temperature advice
        if temp > 35:
            advice.append("It's very hot! Stay hydrated and avoid outdoor activities during peak hours.")
        elif temp > 30:
            advice.append("It's warm. Wear light clothing and stay hydrated.")
        elif temp < 10:
            advice.append("It's cold. Wear warm clothing and layer up.")
        elif temp < 5:
            advice.append("It's very cold! Wear heavy winter clothing and limit outdoor activities.")
        
        # Weather condition advice
        if "rain" in description:
            advice.append("Bring an umbrella and rain gear.")
        elif "snow" in description:
            advice.append("Roads might be slippery. Drive carefully if traveling by vehicle.")
        elif "thunderstorm" in description:
            advice.append("Consider postponing outdoor activities due to thunderstorms.")
        elif "clear" in description:
            advice.append("Perfect weather for outdoor activities!")
        
        # Wind advice
        if wind_speed > 20:
            advice.append("Strong winds expected. Secure loose items and be cautious outdoors.")
        elif wind_speed > 10:
            advice.append("Moderate winds. Consider this when planning outdoor activities.")
        
        return " ".join(advice) if advice else "Weather conditions are suitable for travel."
        
    except Exception as e:
        logger.error(f"Error generating weather advice: {e}")
        return "Weather information available but unable to generate specific advice." 