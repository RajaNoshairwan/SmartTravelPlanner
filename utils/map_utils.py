"""
Map utilities module for travel planning.

This module provides functions for creating interactive maps with travel routes
and points of interest.
"""

import folium
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
CITIES_CSV = DATA_DIR / "cities.csv"

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

def load_city_coordinates() -> Dict[str, Tuple[float, float]]:
    """Load city coordinates from CSV or use default data."""
    try:
        if CITIES_CSV.exists():
            df = pd.read_csv(CITIES_CSV)
            return dict(zip(df['city'], zip(df['latitude'], df['longitude'])))
        return DEFAULT_COORDINATES
    except Exception as e:
        logger.error(f"Error loading city coordinates: {e}")
        return DEFAULT_COORDINATES

def get_city_coordinates(city: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates for a specific city.
    
    Args:
        city (str): Name of the city
        
    Returns:
        Optional[Tuple[float, float]]: Latitude and longitude coordinates
    """
    try:
        coordinates = load_city_coordinates()
        return coordinates.get(city)
    except Exception as e:
        logger.error(f"Error getting coordinates for {city}: {e}")
        return None

def create_travel_map(
    origin: str,
    destination: str,
    attractions: Optional[List[Dict]] = None,
    restaurants: Optional[List[Dict]] = None,
    zoom_start: int = 6
) -> folium.Map:
    """
    Create an interactive map showing the travel route and points of interest.
    
    Args:
        origin (str): Origin city
        destination (str): Destination city
        attractions (Optional[List[Dict]]): List of attractions to display
        restaurants (Optional[List[Dict]]): List of restaurants to display
        zoom_start (int): Initial zoom level
        
    Returns:
        folium.Map: Interactive map object
    """
    try:
        # Get coordinates
        origin_coords = get_city_coordinates(origin)
        dest_coords = get_city_coordinates(destination)
        
        if not origin_coords or not dest_coords:
            raise ValueError("Could not get coordinates for origin or destination")
        
        # Create map centered between origin and destination
        center_lat = (origin_coords[0] + dest_coords[0]) / 2
        center_lon = (origin_coords[1] + dest_coords[1]) / 2
        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start)
        
        # Add origin marker
        folium.Marker(
            location=origin_coords,
            popup=f"Origin: {origin}",
            icon=folium.Icon(color='green', icon='info-sign')
        ).add_to(m)
        
        # Add destination marker
        folium.Marker(
            location=dest_coords,
            popup=f"Destination: {destination}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        # Draw route line
        folium.PolyLine(
            locations=[origin_coords, dest_coords],
            color='blue',
            weight=2,
            opacity=0.8
        ).add_to(m)
        
        # Add attractions if provided
        if attractions:
            for attraction in attractions:
                if 'location' in attraction and attraction['location']:
                    # Try to get coordinates from location string
                    try:
                        # This is a simplified version - in a real app, you'd want to use
                        # a geocoding service to convert addresses to coordinates
                        coords = get_city_coordinates(destination)
                        if coords:
                            folium.Marker(
                                location=coords,
                                popup=f"{attraction['name']}<br>{attraction['description']}",
                                icon=folium.Icon(color='purple', icon='star')
                            ).add_to(m)
                    except Exception as e:
                        logger.error(f"Error adding attraction marker: {e}")
        
        # Add restaurants if provided
        if restaurants:
            for restaurant in restaurants:
                if 'location' in restaurant and restaurant['location']:
                    try:
                        # Similar to attractions, use geocoding in a real app
                        coords = get_city_coordinates(destination)
                        if coords:
                            folium.Marker(
                                location=coords,
                                popup=f"{restaurant['name']}<br>{restaurant['cuisine']}<br>{restaurant['specialties']}",
                                icon=folium.Icon(color='orange', icon='cutlery')
                            ).add_to(m)
                    except Exception as e:
                        logger.error(f"Error adding restaurant marker: {e}")
        
        return m
        
    except Exception as e:
        logger.error(f"Error creating travel map: {e}")
        # Return a basic map centered on Pakistan
        return folium.Map(location=[30.3753, 69.3451], zoom_start=6) 