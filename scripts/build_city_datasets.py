import pandas as pd
import numpy as np
from faker import Faker
from pathlib import Path
import random
from typing import List, Dict, Tuple
import logging
from datetime import datetime
import sys

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.distance_calculator import calculate_distance

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker('en_PK')

# Constants
DATA_DIR = Path(__file__).parent.parent / 'data'
CITIES_FILE = DATA_DIR / 'cities.csv'

# Attraction categories with real examples
ATTRACTION_CATEGORIES = {
    'Historical': ['Fort', 'Tomb', 'Mosque', 'Palace', 'Museum', 'Monument'],
    'Natural': ['Park', 'Garden', 'Lake', 'Mountain', 'Valley', 'Waterfall'],
    'Cultural': ['Bazaar', 'Market', 'Shrine', 'Temple', 'Cultural Center'],
    'Modern': ['Mall', 'Theme Park', 'Aquarium', 'Zoo', 'Science Center']
}

# Restaurant cuisines with specialties
CUISINES = {
    'Pakistani': ['Karahi', 'Biryani', 'Nihari', 'Seekh Kebab', 'Haleem'],
    'Chinese': ['Noodles', 'Fried Rice', 'Dim Sum', 'Wonton', 'Spring Rolls'],
    'Italian': ['Pizza', 'Pasta', 'Risotto', 'Lasagna', 'Tiramisu'],
    'Fast Food': ['Burger', 'Sandwich', 'Fries', 'Chicken Wings', 'Shawarma'],
    'BBQ': ['Tikka', 'Seekh Kebab', 'Malai Boti', 'Chapli Kebab', 'Grilled Fish']
}

# Hotel categories with amenities
HOTEL_CATEGORIES = {
    'Budget': ['WiFi', 'Parking', '24/7 Front Desk'],
    'Business': ['WiFi', 'Breakfast', 'Parking', 'Business Center', 'Gym'],
    'Luxury': ['WiFi', 'Breakfast', 'Parking', 'Pool', 'Spa', 'Restaurant', 'Room Service'],
    'Heritage': ['WiFi', 'Breakfast', 'Parking', 'Garden', 'Cultural Activities'],
    'Resort': ['WiFi', 'Breakfast', 'Parking', 'Pool', 'Spa', 'Restaurant', 'Activities']
}

def load_cities() -> pd.DataFrame:
    """Load cities data."""
    return pd.read_csv(CITIES_FILE)

def generate_attractions(cities_df: pd.DataFrame) -> pd.DataFrame:
    """Generate attractions data for each city."""
    attractions = []
    
    # Real attractions for major cities
    real_attractions = {
        'islamabad': [
            ('Faisal Mosque', 'Historical', 'Largest mosque in Pakistan, modern Islamic architecture', 4.8, 0),
            ('Pakistan Monument', 'Historical', 'National monument symbolizing unity', 4.5, 50),
            ('Daman-e-Koh', 'Natural', 'Scenic viewpoint overlooking Islamabad', 4.6, 0),
            ('Lok Virsa Museum', 'Cultural', 'Museum of Pakistani folk heritage', 4.3, 100),
            ('Margalla Hills', 'Natural', 'Beautiful hiking trails and nature', 4.7, 0)
        ],
        'lahore': [
            ('Badshahi Mosque', 'Historical', 'One of the world\'s largest mosques', 4.9, 0),
            ('Lahore Fort', 'Historical', 'UNESCO World Heritage Site', 4.8, 500),
            ('Shalimar Gardens', 'Historical', 'Mughal-era gardens', 4.6, 200),
            ('Lahore Museum', 'Cultural', 'Ancient artifacts and art', 4.4, 100),
            ('Wagah Border', 'Cultural', 'Famous border ceremony', 4.7, 0)
        ],
        'karachi': [
            ('Mohatta Palace', 'Historical', 'Beautiful palace museum', 4.5, 200),
            ('Clifton Beach', 'Natural', 'Popular beach destination', 4.3, 0),
            ('National Museum', 'Cultural', 'Pakistan\'s largest museum', 4.4, 100),
            ('Empress Market', 'Cultural', 'Historic market building', 4.6, 0),
            ('Churna Island', 'Natural', 'Scuba diving spot', 4.7, 1000)
        ]
    }
    
    for _, city_row in cities_df.iterrows():
        city = city_row['city'].lower()
        
        # Use real attractions for major cities, generate for others
        if city in real_attractions:
            city_attractions = real_attractions[city]
        else:
            city_attractions = []
            for _ in range(5):
                category = random.choice(list(ATTRACTION_CATEGORIES.keys()))
                subcategory = random.choice(ATTRACTION_CATEGORIES[category])
                name = f"{city.title()} {subcategory}"
                description = fake.text(max_nb_chars=100)
                rating = round(random.uniform(3.5, 5.0), 1)
                entry_fee = random.choice([0, 50, 100, 200, 300, 500])
                city_attractions.append((name, category, description, rating, entry_fee))
        
        for name, category, description, rating, entry_fee in city_attractions:
            attractions.append({
                'city': city_row['city'],
                'name': name,
                'category': category,
                'description': description,
                'rating': rating,
                'entry_fee': entry_fee,
                'location': f"{fake.street_address()}, {city_row['city']}"
            })
    
    return pd.DataFrame(attractions)

def generate_restaurants(cities_df: pd.DataFrame) -> pd.DataFrame:
    """Generate restaurants data for each city."""
    restaurants = []
    
    # Real restaurants for major cities
    real_restaurants = {
        'islamabad': [
            ('Monal Restaurant', 'Pakistani', 'Karahi;BBQ;Kebab', 4.7, 'Rs 2000-3000'),
            ('Chaaye Khana', 'Pakistani', 'Tea;Snacks;Breakfast', 4.5, 'Rs 500-1000'),
            ('Kabul Restaurant', 'Pakistani', 'Karahi;Pulao;BBQ', 4.6, 'Rs 1000-2000'),
            ('Ginyaki', 'Chinese', 'Sushi;Noodles;Dim Sum', 4.4, 'Rs 1500-2500'),
            ('Cafe Flo', 'Italian', 'Pizza;Pasta;Desserts', 4.3, 'Rs 2000-3000')
        ],
        'lahore': [
            ('Cuckoo\'s Den', 'Pakistani', 'Traditional Food;BBQ', 4.8, 'Rs 1500-2500'),
            ('Butt Karahi', 'Pakistani', 'Karahi;BBQ', 4.7, 'Rs 1000-2000'),
            ('Cafe Aylanto', 'Italian', 'Pasta;Pizza;Steak', 4.6, 'Rs 2000-3000'),
            ('Gourmet', 'Pakistani', 'BBQ;Karahi;Biryani', 4.5, 'Rs 1000-2000'),
            ('Spice Bazaar', 'Pakistani', 'Traditional;BBQ;Karahi', 4.4, 'Rs 1500-2500')
        ]
    }
    
    price_ranges = ['Rs 500-1000', 'Rs 1000-1500', 'Rs 1500-2000', 'Rs 2000-3000', 'Rs 3000-5000']
    
    for _, city_row in cities_df.iterrows():
        city = city_row['city'].lower()
        
        # Use real restaurants for major cities, generate for others
        if city in real_restaurants:
            city_restaurants = real_restaurants[city]
        else:
            city_restaurants = []
            for _ in range(5):
                cuisine = random.choice(list(CUISINES.keys()))
                specialties = ';'.join(random.sample(CUISINES[cuisine], 3))
                name = f"{fake.company()} {cuisine} Restaurant"
                rating = round(random.uniform(3.0, 5.0), 1)
                price_range = random.choice(price_ranges)
                city_restaurants.append((name, cuisine, specialties, rating, price_range))
        
        for name, cuisine, specialties, rating, price_range in city_restaurants:
            restaurants.append({
                'city': city_row['city'],
                'name': name,
                'cuisine': cuisine,
                'specialties': specialties,
                'rating': rating,
                'price_range': price_range
            })
    
    return pd.DataFrame(restaurants)

def generate_hotels(cities_df: pd.DataFrame) -> pd.DataFrame:
    """Generate hotels data for each city."""
    hotels = []
    
    # Real hotels for major cities
    real_hotels = {
        'islamabad': [
            ('Serena Hotel', 'Luxury', 15000, 4.8, 'Diplomatic Enclave', 'Luxury hotel with spa and fine dining', 'WiFi;Breakfast;Pool;Spa;Restaurant;Room Service'),
            ('Islamabad Hotel', 'Business', 8000, 4.2, 'Blue Area', 'Business hotel in city center', 'WiFi;Breakfast;Parking;Business Center'),
            ('Shelton\'s Hotel', 'Budget', 4000, 3.8, 'F-7', 'Comfortable budget accommodation', 'WiFi;Parking;24/7 Front Desk')
        ],
        'lahore': [
            ('Pearl Continental', 'Luxury', 18000, 4.7, 'Mall Road', 'Five-star luxury hotel', 'WiFi;Breakfast;Pool;Spa;Restaurant;Room Service'),
            ('Nishat Hotel', 'Business', 10000, 4.3, 'Gulberg', 'Business hotel with modern amenities', 'WiFi;Breakfast;Parking;Business Center;Gym'),
            ('Hotel One', 'Budget', 5000, 3.9, 'Main Boulevard', 'Affordable comfort', 'WiFi;Breakfast;Parking;24/7 Front Desk')
        ]
    }
    
    for _, city_row in cities_df.iterrows():
        city = city_row['city'].lower()
        
        # Use real hotels for major cities, generate for others
        if city in real_hotels:
            city_hotels = real_hotels[city]
        else:
            city_hotels = []
            for _ in range(3):
                category = random.choice(list(HOTEL_CATEGORIES.keys()))
                name = f"{fake.company()} Hotel"
                price = random.randint(3000, 20000)
                rating = round(random.uniform(3.0, 5.0), 1)
                location = f"{fake.street_address()}, {city_row['city']}"
                description = fake.text(max_nb_chars=100)
                amenities = ';'.join(HOTEL_CATEGORIES[category])
                city_hotels.append((name, category, price, rating, location, description, amenities))
        
        for i, (name, category, price, rating, location, description, amenities) in enumerate(city_hotels, 1):
            hotels.append({
                'city': city_row['city'],
                'hotel_id': f"{city[:3].upper()}{i:03d}",
                'name': name,
                'price_per_night': price,
                'rating': rating,
                'category': category,
                'location': location,
                'description': description,
                'amenities': amenities
            })
    
    return pd.DataFrame(hotels)

def generate_travel_costs(cities_df: pd.DataFrame) -> pd.DataFrame:
    """Generate travel costs between cities."""
    travel_costs = []
    cities = cities_df['city'].tolist()
    
    for i, origin in enumerate(cities):
        for destination in cities[i+1:]:  # Only generate one direction
            # Calculate distance using city names (not coordinates)
            distance = calculate_distance(origin, destination)
            
            # Calculate costs
            car_cost = int(distance * 12)
            bus_cost = int(distance * 8)
            train_cost = int(distance * 6)
            flight_cost = max(5000, int(distance * 25))
            
            travel_costs.append({
                'origin': origin,
                'destination': destination,
                'car': car_cost,
                'bus': bus_cost,
                'train': train_cost,
                'flight': flight_cost
            })
    
    return pd.DataFrame(travel_costs)

def main():
    """Main function to generate all datasets."""
    logger.info("Starting dataset generation...")
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load cities
    cities_df = load_cities()
    num_cities = len(cities_df)
    
    # Generate datasets
    attractions_df = generate_attractions(cities_df)
    restaurants_df = generate_restaurants(cities_df)
    hotels_df = generate_hotels(cities_df)
    travel_costs_df = generate_travel_costs(cities_df)
    
    # Save datasets
    attractions_df.to_csv(DATA_DIR / 'attractions.csv', index=False)
    restaurants_df.to_csv(DATA_DIR / 'restaurants.csv', index=False)
    hotels_df.to_csv(DATA_DIR / 'hotels.csv', index=False)
    travel_costs_df.to_csv(DATA_DIR / 'travel_costs.csv', index=False)
    
    # Log summary
    logger.info(f"Generated datasets:")
    logger.info(f"- {num_cities} cities × {len(attractions_df)/num_cities:.1f} attractions")
    logger.info(f"- {num_cities} cities × {len(restaurants_df)/num_cities:.1f} restaurants")
    logger.info(f"- {num_cities} cities × {len(hotels_df)/num_cities:.1f} hotels")
    logger.info(f"- {len(travel_costs_df)} travel cost pairs")
    logger.info("Dataset generation complete!")

if __name__ == '__main__':
    main() 