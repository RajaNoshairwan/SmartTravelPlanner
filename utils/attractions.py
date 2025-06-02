"""
Attractions module for travel planning.

This module provides information about tourist attractions and restaurants in Pakistan.
"""

from typing import Dict, List
import logging
from pathlib import Path
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
ATTRACTIONS_CSV = DATA_DIR / "attractions.csv"
RESTAURANTS_CSV = DATA_DIR / "restaurants.csv"

# Default attractions data if CSV is not available
DEFAULT_ATTRACTIONS = {
    "Islamabad": [
        {
            "name": "Faisal Mosque",
            "description": "One of the largest mosques in the world, known for its unique modern design",
            "category": "Religious",
            "rating": 4.8,
            "location": "Shah Faisal Avenue, Islamabad",
            "best_time": "Morning and Evening",
            "entry_fee": "Free"
        },
        {
            "name": "Pakistan Monument",
            "description": "National monument representing the four provinces of Pakistan",
            "category": "Historical",
            "rating": 4.5,
            "location": "Shakarparian Hills, Islamabad",
            "best_time": "Evening",
            "entry_fee": "Rs. 20"
        },
        {
            "name": "Daman-e-Koh",
            "description": "Scenic viewpoint offering panoramic views of Islamabad",
            "category": "Nature",
            "rating": 4.6,
            "location": "Margalla Hills, Islamabad",
            "best_time": "Sunset",
            "entry_fee": "Free"
        }
    ],
    "Lahore": [
        {
            "name": "Badshahi Mosque",
            "description": "One of the world's largest mosques, built during the Mughal era",
            "category": "Religious",
            "rating": 4.9,
            "location": "Walled City, Lahore",
            "best_time": "Morning and Evening",
            "entry_fee": "Free"
        },
        {
            "name": "Lahore Fort",
            "description": "Historic fort complex with beautiful architecture and gardens",
            "category": "Historical",
            "rating": 4.7,
            "location": "Walled City, Lahore",
            "best_time": "Morning",
            "entry_fee": "Rs. 40"
        },
        {
            "name": "Shalimar Gardens",
            "description": "UNESCO World Heritage Site, famous Mughal gardens",
            "category": "Historical",
            "rating": 4.6,
            "location": "Grand Trunk Road, Lahore",
            "best_time": "Morning",
            "entry_fee": "Rs. 30"
        }
    ],
    "Karachi": [
        {
            "name": "Clifton Beach",
            "description": "Popular beach with recreational activities and food stalls",
            "category": "Nature",
            "rating": 4.3,
            "location": "Clifton, Karachi",
            "best_time": "Evening",
            "entry_fee": "Free"
        },
        {
            "name": "Mohatta Palace",
            "description": "Historic palace with museum showcasing art and culture",
            "category": "Museum",
            "rating": 4.5,
            "location": "Clifton, Karachi",
            "best_time": "Morning",
            "entry_fee": "Rs. 50"
        },
        {
            "name": "Port Grand",
            "description": "Food street and entertainment complex by the harbor",
            "category": "Entertainment",
            "rating": 4.4,
            "location": "Kemari, Karachi",
            "best_time": "Evening",
            "entry_fee": "Rs. 100"
        }
    ]
}

# Default restaurants data if CSV is not available
DEFAULT_RESTAURANTS = {
    "Islamabad": [
        {
            "name": "Monal Restaurant",
            "cuisine": "Pakistani",
            "rating": 4.5,
            "price_range": "$$$",
            "location": "Pir Sohawa Road, Islamabad",
            "specialties": ["Karahi", "BBQ", "Traditional Pakistani"],
            "best_for": "Dinner with a view"
        },
        {
            "name": "Chaaye Khana",
            "cuisine": "Pakistani",
            "rating": 4.3,
            "price_range": "$$",
            "location": "F-7 Markaz, Islamabad",
            "specialties": ["Tea", "Breakfast", "Desi Food"],
            "best_for": "Breakfast and Tea"
        }
    ],
    "Lahore": [
        {
            "name": "Cafe Aylanto",
            "cuisine": "International",
            "rating": 4.6,
            "price_range": "$$$",
            "location": "Gulberg, Lahore",
            "specialties": ["Italian", "Mediterranean", "Grilled"],
            "best_for": "Fine Dining"
        },
        {
            "name": "Butt Karahi",
            "cuisine": "Pakistani",
            "rating": 4.7,
            "price_range": "$$",
            "location": "Mall Road, Lahore",
            "specialties": ["Karahi", "BBQ"],
            "best_for": "Traditional Food"
        }
    ],
    "Karachi": [
        {
            "name": "Kolachi",
            "cuisine": "Pakistani",
            "rating": 4.5,
            "price_range": "$$$",
            "location": "Do Darya, Karachi",
            "specialties": ["Seafood", "BBQ", "Traditional"],
            "best_for": "Seafood and Sunset Views"
        },
        {
            "name": "Xander's",
            "cuisine": "International",
            "rating": 4.4,
            "price_range": "$$$",
            "location": "Clifton, Karachi",
            "specialties": ["Steaks", "Burgers", "Pasta"],
            "best_for": "International Cuisine"
        }
    ]
}

def load_attractions_data() -> Dict[str, List[Dict]]:
    """Load attractions data from CSV or use default data."""
    try:
        if ATTRACTIONS_CSV.exists():
            df = pd.read_csv(ATTRACTIONS_CSV)
            attractions = {}
            for city in df['city'].unique():
                city_data = df[df['city'] == city]
                attractions[city] = city_data.to_dict('records')
            return attractions
        return DEFAULT_ATTRACTIONS
    except Exception as e:
        logger.error(f"Error loading attractions data: {e}")
        return DEFAULT_ATTRACTIONS

def load_restaurants_data() -> Dict[str, List[Dict]]:
    """Load restaurants data from CSV or use default data."""
    try:
        if RESTAURANTS_CSV.exists():
            df = pd.read_csv(RESTAURANTS_CSV)
            restaurants = {}
            for city in df['city'].unique():
                city_data = df[df['city'] == city]
                restaurants[city] = city_data.to_dict('records')
            return restaurants
        return DEFAULT_RESTAURANTS
    except Exception as e:
        logger.error(f"Error loading restaurants data: {e}")
        return DEFAULT_RESTAURANTS

def get_attractions(city: str) -> List[Dict]:
    """
    Get attractions for a specific city.
    
    Args:
        city (str): Name of the city
        
    Returns:
        List[Dict]: List of attractions with details
    """
    try:
        attractions_data = load_attractions_data()
        return attractions_data.get(city, attractions_data.get("Islamabad", []))
    except Exception as e:
        logger.error(f"Error getting attractions for {city}: {e}")
        return []

def get_restaurants(city: str) -> List[Dict]:
    """
    Get restaurants for a specific city.
    
    Args:
        city (str): Name of the city
        
    Returns:
        List[Dict]: List of restaurants with details
    """
    try:
        restaurants_data = load_restaurants_data()
        return restaurants_data.get(city, restaurants_data.get("Islamabad", []))
    except Exception as e:
        logger.error(f"Error getting restaurants for {city}: {e}")
        return []

def get_top_attractions(city: str, limit: int = 5) -> List[Dict]:
    """
    Get top-rated attractions for a specific city.
    
    Args:
        city (str): Name of the city
        limit (int): Maximum number of attractions to return
        
    Returns:
        List[Dict]: List of top attractions
    """
    try:
        attractions = get_attractions(city)
        # Sort by rating and return top attractions
        sorted_attractions = sorted(attractions, key=lambda x: x.get('rating', 0), reverse=True)
        return sorted_attractions[:limit]
    except Exception as e:
        logger.error(f"Error getting top attractions for {city}: {e}")
        return []

def get_top_restaurants(city: str, limit: int = 5) -> List[Dict]:
    """
    Get top-rated restaurants for a specific city.
    
    Args:
        city (str): Name of the city
        limit (int): Maximum number of restaurants to return
        
    Returns:
        List[Dict]: List of top restaurants
    """
    try:
        restaurants = get_restaurants(city)
        # Sort by rating and return top restaurants
        sorted_restaurants = sorted(restaurants, key=lambda x: x.get('rating', 0), reverse=True)
        return sorted_restaurants[:limit]
    except Exception as e:
        logger.error(f"Error getting top restaurants for {city}: {e}")
        return [] 