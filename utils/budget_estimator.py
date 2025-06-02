"""
Budget estimator module for travel planning.

This module provides functions to estimate travel costs, accommodation costs,
and total budget for trips in Pakistan.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional
import logging
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = Path(__file__).parent.parent / "data"
TRAVEL_COSTS_CSV = DATA_DIR / "travel_costs.csv"
HOTELS_CSV = DATA_DIR / "hotels.csv"

# Default costs
DEFAULT_FOOD_COST = 2000  # Rs. per person per day
DEFAULT_ACTIVITIES_COST = 1500  # Rs. per person per day
DEFAULT_FUEL_PRICE = 280.0  # Rs. per liter
DEFAULT_BUS_COST_PER_KM = 2.5  # Rs. per km
DEFAULT_FLIGHT_COST_PER_KM = 15.0  # Rs. per km

# Bus ticket prices for major routes (Rs.)
BUS_TICKET_PRICES = {
    ("Islamabad", "Lahore"): 1200,
    ("Islamabad", "Karachi"): 3500,
    ("Islamabad", "Peshawar"): 800,
    ("Lahore", "Karachi"): 3000,
    ("Lahore", "Multan"): 1000,
    ("Karachi", "Hyderabad"): 500,
    ("Peshawar", "Islamabad"): 800,
    ("Quetta", "Karachi"): 2500,
    ("Faisalabad", "Lahore"): 800,
    ("Multan", "Lahore"): 1000,
}

def load_travel_costs() -> pd.DataFrame:
    """Load travel costs data from CSV."""
    try:
        return pd.read_csv(TRAVEL_COSTS_CSV)
    except Exception as e:
        logger.error(f"Error loading travel costs: {e}")
        return pd.DataFrame()

def load_hotel_data() -> pd.DataFrame:
    """Load hotel data from CSV."""
    try:
        return pd.read_csv(HOTELS_CSV)
    except Exception as e:
        logger.error(f"Error loading hotel data: {e}")
        return pd.DataFrame()

def get_bus_ticket_price(origin: str, destination: str) -> float:
    """Get bus ticket price for a route."""
    # Try to find exact route
    route = (origin, destination)
    if route in BUS_TICKET_PRICES:
        return BUS_TICKET_PRICES[route]
    
    # Try reverse route
    reverse_route = (destination, origin)
    if reverse_route in BUS_TICKET_PRICES:
        return BUS_TICKET_PRICES[reverse_route]
    
    # If no specific price found, estimate based on distance
    try:
        from utils.distance_calculator import calculate_distance
        distance = calculate_distance(origin, destination)
        return distance * DEFAULT_BUS_COST_PER_KM
    except Exception as e:
        logger.error(f"Error calculating bus ticket price: {e}")
        return 0.0

def calculate_vehicle_cost(distance: float, fuel_efficiency: float, fuel_price: float) -> float:
    """Calculate vehicle travel cost based on distance and fuel efficiency."""
    try:
        fuel_required = distance / fuel_efficiency
        return fuel_required * fuel_price
    except Exception as e:
        logger.error(f"Error calculating vehicle cost: {e}")
        return 0.0

def get_travel_costs(origin: str, destination: str, mode: str, 
                    fuel_efficiency: Optional[float] = None,
                    fuel_price: float = DEFAULT_FUEL_PRICE) -> float:
    """Calculate travel costs based on mode of transportation."""
    try:
        from utils.distance_calculator import calculate_distance
        distance = calculate_distance(origin, destination)
        
        if mode == "vehicle":
            if not fuel_efficiency:
                raise ValueError("Fuel efficiency required for vehicle mode")
            km_per_litre = fuel_efficiency
            litres_needed = distance / km_per_litre
            return litres_needed * fuel_price
        
        elif mode == "bus":
            return get_bus_ticket_price(origin, destination)
        
        elif mode == "flight":
            # Estimate flight cost based on distance
            return distance * DEFAULT_FLIGHT_COST_PER_KM
        
        else:
            raise ValueError(f"Invalid travel mode: {mode}")
            
    except Exception as e:
        logger.error(f"Error calculating travel costs: {e}")
        return 0.0

def get_hotels_in_city(city: str) -> pd.DataFrame:
    """Get list of hotels in a city."""
    try:
        df = load_hotel_data()
        if df.empty:
            return pd.DataFrame()
        
        # Filter hotels by city and sort by rating and price
        city_hotels = df[df['city'].str.lower() == city.lower()].copy()
        city_hotels = city_hotels.sort_values(['rating', 'price_per_night'], ascending=[False, True])
        return city_hotels
        
    except Exception as e:
        logger.error(f"Error getting hotels in {city}: {e}")
        return pd.DataFrame()

def get_hotel_cost_by_id(hotel_id: str, nights: int) -> Dict[str, float]:
    """Get hotel cost for a specific hotel."""
    try:
        df = load_hotel_data()
        if df.empty:
            return {"price_per_night": 0.0, "total": 0.0}
        
        hotel = df[df['hotel_id'] == hotel_id]
        if hotel.empty:
            return {"price_per_night": 0.0, "total": 0.0}
        
        price_per_night = hotel.iloc[0]['price_per_night']
        return {
            "price_per_night": price_per_night,
            "total": price_per_night * nights
        }
        
    except Exception as e:
        logger.error(f"Error getting hotel cost for {hotel_id}: {e}")
        return {"price_per_night": 0.0, "total": 0.0}

def estimate_total_budget(
    origin: str,
    destination: str,
    nights: int,
    travelers: int,
    mode: str,
    fuel_efficiency: Optional[float] = None,
    fuel_price: float = DEFAULT_FUEL_PRICE,
    hotel_id: Optional[str] = None
) -> Dict[str, float]:
    """Estimate total budget for the trip."""
    try:
        # Calculate transportation costs
        transportation = get_travel_costs(
            origin=origin,
            destination=destination,
            mode=mode,
            fuel_efficiency=fuel_efficiency,
            fuel_price=fuel_price
        )
        
        # Calculate accommodation costs
        if hotel_id:
            hotel_costs = get_hotel_cost_by_id(hotel_id, nights)
            # One room can host up to 2 people
            rooms_needed = math.ceil(travelers / 2)
            accommodation = hotel_costs["total"] * rooms_needed
        else:
            # Use default hotel cost if no hotel selected
            # One room can host up to 2 people
            rooms_needed = math.ceil(travelers / 2)
            accommodation = 5000 * nights * rooms_needed  # Rs. 5000 per night per room
        
        # Calculate food costs
        food = DEFAULT_FOOD_COST * travelers
        
        # Calculate activities costs
        activities = DEFAULT_ACTIVITIES_COST * travelers
        
        # Calculate total
        total = transportation + accommodation + (food * nights) + (activities * nights)
        
        return {
            "transportation": transportation,
            "accommodation": accommodation,
            "food": food,
            "activities": activities,
            "nights": nights,
            "total": total
        }
        
    except Exception as e:
        logger.error(f"Error estimating budget: {e}")
        return {
            "transportation": 0.0,
            "accommodation": 0.0,
            "food": DEFAULT_FOOD_COST,
            "activities": DEFAULT_ACTIVITIES_COST,
            "nights": nights,
            "total": 0.0
        } 