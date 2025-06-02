import pandas as pd
import pytest
from pathlib import Path

# Constants
DATA_DIR = Path(__file__).parent.parent / 'data'

def load_cities():
    """Load cities data."""
    return pd.read_csv(DATA_DIR / 'cities.csv')

def test_all_cities_have_content():
    """Test that all cities have the required number of entries in each dataset."""
    cities = load_cities().city.str.lower().tolist()
    
    # Load datasets
    attractions = pd.read_csv(DATA_DIR / 'attractions.csv')
    restaurants = pd.read_csv(DATA_DIR / 'restaurants.csv')
    hotels = pd.read_csv(DATA_DIR / 'hotels.csv')
    
    # Convert city names to lowercase for comparison
    attractions['city'] = attractions.city.str.lower()
    restaurants['city'] = restaurants.city.str.lower()
    hotels['city'] = hotels.city.str.lower()
    
    # Test each city
    for city in cities:
        # Test attractions
        city_attractions = attractions[attractions.city == city]
        assert len(city_attractions) >= 5, f"{city} has only {len(city_attractions)} attractions (minimum 5 required)"
        
        # Test restaurants
        city_restaurants = restaurants[restaurants.city == city]
        assert len(city_restaurants) >= 5, f"{city} has only {len(city_restaurants)} restaurants (minimum 5 required)"
        
        # Test hotels
        city_hotels = hotels[hotels.city == city]
        assert len(city_hotels) >= 3, f"{city} has only {len(city_hotels)} hotels (minimum 3 required)"
        
        # Test attraction data quality
        assert all(city_attractions.rating.between(3.5, 5.0)), f"{city} has attractions with ratings outside 3.5-5.0 range"
        assert all(city_attractions.entry_fee.between(0, 500)), f"{city} has attractions with entry fees outside 0-500 PKR range"
        
        # Test restaurant data quality
        assert all(city_restaurants.rating.between(3.0, 5.0)), f"{city} has restaurants with ratings outside 3.0-5.0 range"
        assert all(city_restaurants.price_range.str.startswith('Rs ')), f"{city} has restaurants with invalid price range format"
        
        # Test hotel data quality
        assert all(city_hotels.rating.between(3.0, 5.0)), f"{city} has hotels with ratings outside 3.0-5.0 range"
        assert all(city_hotels.price_per_night.between(3000, 20000)), f"{city} has hotels with prices outside 3000-20000 PKR range"
        assert all(city_hotels.category.isin(['Budget', 'Business', 'Luxury', 'Heritage', 'Resort'])), f"{city} has hotels with invalid categories"

def test_travel_cost_matrix():
    """Test that travel costs exist for all city pairs."""
    cities = load_cities().city.str.lower().tolist()
    travel_costs = pd.read_csv(DATA_DIR / 'travel_costs.csv')
    
    # Convert city names to lowercase for comparison
    travel_costs['origin'] = travel_costs.origin.str.lower()
    travel_costs['destination'] = travel_costs.destination.str.lower()
    
    # Test each city pair
    for origin in cities:
        for destination in cities:
            if origin != destination:
                # Check if either direction exists
                pair_exists = (
                    ((travel_costs.origin == origin) & (travel_costs.destination == destination)) |
                    ((travel_costs.origin == destination) & (travel_costs.destination == origin))
                ).any()
                
                assert pair_exists, f"Missing travel costs for {origin} <-> {destination}"
                
                # If pair exists, test cost values
                if pair_exists:
                    costs = travel_costs[
                        ((travel_costs.origin == origin) & (travel_costs.destination == destination)) |
                        ((travel_costs.origin == destination) & (travel_costs.destination == origin))
                    ].iloc[0]
                    
                    # Test cost relationships
                    assert costs.car > costs.bus, f"Car cost should be higher than bus cost for {origin} <-> {destination}"
                    assert costs.bus > costs.train, f"Bus cost should be higher than train cost for {origin} <-> {destination}"
                    assert costs.flight >= 5000, f"Flight cost should be at least 5000 PKR for {origin} <-> {destination}"
                    assert costs.flight > costs.car, f"Flight cost should be higher than car cost for {origin} <-> {destination}"

def test_data_consistency():
    """Test that all datasets are consistent with each other."""
    cities = load_cities().city.str.lower().tolist()
    
    # Load all datasets
    attractions = pd.read_csv(DATA_DIR / 'attractions.csv')
    restaurants = pd.read_csv(DATA_DIR / 'restaurants.csv')
    hotels = pd.read_csv(DATA_DIR / 'hotels.csv')
    travel_costs = pd.read_csv(DATA_DIR / 'travel_costs.csv')
    
    # Convert city names to lowercase
    for df in [attractions, restaurants, hotels, travel_costs]:
        if 'city' in df.columns:
            df['city'] = df.city.str.lower()
        if 'origin' in df.columns:
            df['origin'] = df.origin.str.lower()
        if 'destination' in df.columns:
            df['destination'] = df.destination.str.lower()
    
    # Test that all cities in datasets exist in cities.csv
    for df, name in [(attractions, 'attractions'), (restaurants, 'restaurants'), (hotels, 'hotels')]:
        dataset_cities = set(df.city.unique())
        assert dataset_cities.issubset(set(cities)), f"Cities in {name} dataset not found in cities.csv: {dataset_cities - set(cities)}"
    
    # Test that all cities in travel costs exist in cities.csv
    travel_cities = set(travel_costs.origin.unique()) | set(travel_costs.destination.unique())
    assert travel_cities.issubset(set(cities)), f"Cities in travel costs not found in cities.csv: {travel_cities - set(cities)}"
    
    # Test that hotel IDs are unique
    assert hotels.hotel_id.nunique() == len(hotels), "Duplicate hotel IDs found"
    
    # Test that hotel IDs follow the correct format (3-letter city code + 3 digits)
    assert all(hotels.hotel_id.str.match(r'^[A-Z]{3}\d{3}$')), "Invalid hotel ID format"
    
    # Test that amenities are properly formatted
    assert all(hotels.amenities.str.contains(';')), "Hotel amenities should be semicolon-separated"
    
    # Test that restaurant specialties are properly formatted
    assert all(restaurants.specialties.str.contains(';')), "Restaurant specialties should be semicolon-separated"
    
    # Test that price ranges follow the correct format
    assert all(restaurants.price_range.str.match(r'^Rs \d+-\d+$')), "Invalid restaurant price range format" 