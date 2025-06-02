"""
Distance calculator module for travel planning.

This module provides functions for calculating distances between cities
and getting route information.
"""

from typing import Dict, Tuple, Optional
import logging
from pathlib import Path
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
CITIES_CSV = DATA_DIR / "cities.csv"
DEFAULT_COUNTRY = "Pakistan"
OSRM_BASE_URL = "http://router.project-osrm.org/route/v1/driving"

# Default city coordinates if CSV is not available
DEFAULT_COORDINATES = {
    "Islamabad": (33.7294, 73.0931),
    "Lahore": (31.5204, 74.3587),
    "Karachi": (24.8607, 67.0011),
    "Peshawar": (34.0150, 71.5249),
    "Quetta": (30.1798, 66.9750),
    "Multan": (30.1575, 71.5249),
    "Faisalabad": (31.4504, 73.1350),
    "Hyderabad": (25.3969, 68.3778),
    "Rawalpindi": (33.6007, 73.0679),
    "Gujranwala": (32.1877, 74.1945)
}

# Average speeds (km/h) for different travel modes
AVG_SPEEDS = {
    "vehicle": 60,  # Average highway speed
    "bus": 50,      # Average bus speed
    "flight": 800   # Average flight speed
}

def get_or_add_city_coordinates(city: str) -> tuple[float, float]:
    """Get city coordinates from CSV or geocode and cache if missing."""
    try:
        df = pd.read_csv(CITIES_CSV)
        match = df[df['city'].str.lower() == city.lower()]
        if not match.empty:
            return float(match.iloc[0]['latitude']), float(match.iloc[0]['longitude'])
        # Not found, geocode
        geolocator = Nominatim(user_agent="travel_planner")
        location = geolocator.geocode(f"{city}, {DEFAULT_COUNTRY}")
        if not location:
            raise ValueError(f"Could not geocode city: {city}")
        new_row = pd.DataFrame({
            'city': [city],
            'country': [DEFAULT_COUNTRY],
            'latitude': [location.latitude],
            'longitude': [location.longitude],
            'province': ['Unknown']
        })
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(CITIES_CSV, index=False)
        return location.latitude, location.longitude
    except Exception as e:
        logger.error(f"Error in get_or_add_city_coordinates: {e}")
        raise

def get_coordinates(city: str) -> tuple[float, float]:
    return get_or_add_city_coordinates(city)

def get_road_distance(origin_coords: Tuple[float, float], dest_coords: Tuple[float, float]) -> Optional[float]:
    """Get actual road distance between two points using OSRM."""
    try:
        # Format coordinates for OSRM API (note: OSRM uses lon,lat order)
        url = f"{OSRM_BASE_URL}/{origin_coords[1]},{origin_coords[0]};{dest_coords[1]},{dest_coords[0]}"
        
        # Make request to OSRM
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data["code"] == "Ok":
            # OSRM returns distance in meters, convert to kilometers
            return round(data["routes"][0]["distance"] / 1000, 1)
        else:
            logger.error(f"OSRM API error: {data.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting road distance: {e}")
        return None

def calculate_distance(origin: str, destination: str) -> float:
    """Calculate actual road distance between two cities in kilometers."""
    try:
        # Get coordinates for both cities
        origin_coords = get_or_add_city_coordinates(origin)
        dest_coords = get_or_add_city_coordinates(destination)
        
        # Try to get road distance first
        road_distance = get_road_distance(origin_coords, dest_coords)
        
        if road_distance is not None:
            logger.info(f"Using road distance for {origin} to {destination}")
            return road_distance
            
        # Fall back to geodesic distance if OSRM fails
        logger.warning(f"Falling back to geodesic distance for {origin} to {destination}")
        return round(geodesic(origin_coords, dest_coords).kilometers, 1)
        
    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        raise

def get_route_info(origin: str, destination: str, mode: str = "vehicle") -> Dict[str, float]:
    """
    Get route information including distance and estimated travel time.
    
    Args:
        origin (str): Origin city name
        destination (str): Destination city name
        mode (str): Travel mode (vehicle, bus, or flight)
        
    Returns:
        Dict[str, float]: Dictionary containing distance and estimated time
    """
    try:
        # Calculate distance
        distance = calculate_distance(origin, destination)
        
        # Get average speed for the travel mode
        speed = AVG_SPEEDS.get(mode, AVG_SPEEDS["vehicle"])
        
        # Calculate estimated time
        time_hours = distance / speed
        
        return {
            "distance": distance,
            "time_hours": round(time_hours, 1)
        }
        
    except Exception as e:
        logger.error(f"Error getting route info: {e}")
        return {
            "distance": 0.0,
            "time_hours": 0.0
        } 