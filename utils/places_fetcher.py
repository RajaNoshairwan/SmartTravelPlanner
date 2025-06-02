"""
Places fetcher module for travel planning.

This module provides functions to fetch information about attractions and restaurants
from the CSV data files.
"""

from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
ATTRACTIONS_CSV = DATA_DIR / "attractions.csv"
RESTAURANTS_CSV = DATA_DIR / "restaurants.csv"

def load_attractions_data() -> pd.DataFrame:
    """Load attractions data from CSV.
    
    Returns:
        pd.DataFrame: DataFrame containing attractions information
    """
    try:
        return pd.read_csv(ATTRACTIONS_CSV)
    except Exception as e:
        logger.error(f"Error loading attractions data: {e}")
        return pd.DataFrame()

def load_restaurants_data() -> pd.DataFrame:
    """Load restaurants data from CSV.
    
    Returns:
        pd.DataFrame: DataFrame containing restaurants information
    """
    try:
        return pd.read_csv(RESTAURANTS_CSV)
    except Exception as e:
        logger.error(f"Error loading restaurants data: {e}")
        return pd.DataFrame()

def get_attractions(city: str, category: Optional[str] = None) -> List[Dict]:
    """Get attractions for a city, optionally filtered by category.
    
    Args:
        city: City name
        category: Optional category to filter by
        
    Returns:
        List[Dict]: List of attractions with their details
    """
    try:
        df = load_attractions_data()
        if df.empty:
            return []
            
        # Filter by city
        city_attractions = df[df['city'].str.lower() == city.lower()]
        
        # Filter by category if specified
        if category:
            city_attractions = city_attractions[
                city_attractions['category'].str.lower() == category.lower()
            ]
            
        if city_attractions.empty:
            return []
            
        # Convert to list of dictionaries
        attractions = []
        for _, row in city_attractions.iterrows():
            attractions.append({
                "name": row['attraction_name'],
                "category": row['category'],
                "rating": float(row['rating']),
                "entry_fee": float(row['entry_fee']),
                "description": row['description']
            })
            
        return attractions
        
    except Exception as e:
        logger.error(f"Error getting attractions: {e}")
        return []

def get_restaurants(
    city: str,
    cuisine: Optional[str] = None,
    price_range: Optional[str] = None
) -> List[Dict]:
    """Get restaurants for a city, optionally filtered by cuisine and price range.
    
    Args:
        city: City name
        cuisine: Optional cuisine type to filter by
        price_range: Optional price range to filter by (Low/Medium/High)
        
    Returns:
        List[Dict]: List of restaurants with their details
    """
    try:
        df = load_restaurants_data()
        if df.empty:
            return []
            
        # Filter by city
        city_restaurants = df[df['city'].str.lower() == city.lower()]
        
        # Filter by cuisine if specified
        if cuisine:
            city_restaurants = city_restaurants[
                city_restaurants['cuisine'].str.lower() == cuisine.lower()
            ]
            
        # Filter by price range if specified
        if price_range:
            city_restaurants = city_restaurants[
                city_restaurants['price_range'].str.lower() == price_range.lower()
            ]
            
        if city_restaurants.empty:
            return []
            
        # Convert to list of dictionaries
        restaurants = []
        for _, row in city_restaurants.iterrows():
            restaurants.append({
                "name": row['restaurant_name'],
                "cuisine": row['cuisine'],
                "rating": float(row['rating']),
                "price_range": row['price_range'],
                "specialties": row['specialties'].split(", ")
            })
            
        return restaurants
        
    except Exception as e:
        logger.error(f"Error getting restaurants: {e}")
        return []

def get_top_attractions(city: str, limit: int = 3) -> List[Dict]:
    """Get top-rated attractions for a city.
    
    Args:
        city: City name
        limit: Maximum number of attractions to return
        
    Returns:
        List[Dict]: List of top attractions
    """
    attractions = get_attractions(city)
    return sorted(attractions, key=lambda x: x['rating'], reverse=True)[:limit]

def get_top_restaurants(city: str, limit: int = 3) -> List[Dict]:
    """Get top-rated restaurants for a city.
    
    Args:
        city: City name
        limit: Maximum number of restaurants to return
        
    Returns:
        List[Dict]: List of top restaurants
    """
    restaurants = get_restaurants(city)
    return sorted(restaurants, key=lambda x: x['rating'], reverse=True)[:limit] 