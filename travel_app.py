"""
Smart Travel Planner - Streamlit App

A modern travel planning application for Pakistan with interactive maps,
budget estimation, and travel information.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import sys
import os
from typing import Optional
import plotly.express as px

# Add utils to path
sys.path.append(str(Path(__file__).parent))

# Import utility modules
from utils.distance_calculator import calculate_distance, get_route_info, get_coordinates
from utils.budget_estimator import (
    estimate_total_budget,
    DEFAULT_FUEL_PRICE,
    get_hotels_in_city,
    get_hotel_cost_by_id,
    get_travel_costs
)
from utils.weather_fetcher import get_weather_info
from utils.safety_info import get_all_safety_info
from utils.places_fetcher import get_top_attractions, get_top_restaurants
from utils.map_utils import create_travel_map
from utils.safety_tips import get_safety_tips
from utils.attractions import get_attractions, get_restaurants

# Constants
DATA_DIR = Path(__file__).parent / "data"
CITIES_CSV = DATA_DIR / "cities.csv"

# Set OpenWeather API key
os.environ["OPENWEATHER_API_KEY"] = "ad9dd2f3e0d38465e08d5b29708471bc"

# Page config
st.set_page_config(
    page_title="Smart Travel Planner - Pakistan",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .budget-breakdown {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    .budget-item {
        display: flex;
        justify-content: space-between;
        padding: 0.75rem 0;
        border-bottom: 1px solid #e9ecef;
    }
    .budget-item:last-child {
        border-bottom: none;
    }
    .budget-total {
        font-weight: bold;
        font-size: 1.2rem;
        color: #1f77b4;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 2px solid #1f77b4;
    }
    .vehicle-details {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    .hotel-card {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
    }
    .hotel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .hotel-rating {
        color: #ffa500;
        font-weight: bold;
    }
    .hotel-price {
        color: #28a745;
        font-weight: bold;
    }
    .hotel-category {
        background-color: #e9ecef;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        display: inline-block;
        margin: 0.5rem 0;
    }
    .weather-card {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_cities() -> list:
    """Load list of cities from CSV."""
    try:
        df = pd.read_csv(CITIES_CSV)
        return sorted(df['city'].unique().tolist())
    except Exception as e:
        st.error(f"Error loading cities: {e}")
        return []

def format_currency(amount: float) -> str:
    """Format amount as Pakistani Rupees."""
    return f"Rs. {amount:,.0f}"

def create_card(title: str, content: str, icon: str = ""):
    """Create a styled card with title and content."""
    st.markdown(f"""
        <div class="stCard">
            <h3>{icon} {title}</h3>
            {content}
        </div>
    """, unsafe_allow_html=True)

def display_weather_info(city: str):
    """Display weather information in a card format."""
    weather_info = get_weather_info(city)
    if weather_info:
        st.markdown('<div class="weather-card">', unsafe_allow_html=True)
        st.markdown(f"### Current Weather in {city}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Temperature",
                f"{weather_info['temperature']}°C",
                f"Feels like {weather_info['feels_like']}°C"
            )
        with col2:
            st.metric(
                "Humidity",
                f"{weather_info['humidity']}%",
                f"Wind: {weather_info['wind_speed']} m/s"
            )
        with col3:
            st.metric(
                "Conditions",
                weather_info['description'].title(),
                f"Updated: {weather_info['last_updated']}"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error(f"Unable to fetch weather information for {city}")

def display_budget_breakdown(budget: dict):
    """Display budget breakdown in a structured format."""
    st.markdown("### Budget Breakdown")
    st.markdown('<div class="budget-breakdown">', unsafe_allow_html=True)
    
    # Transportation
    st.markdown("#### Transportation")
    st.markdown('<div class="budget-item">', unsafe_allow_html=True)
    st.markdown(f"**Travel Cost:** {format_currency(budget['transportation'])}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Accommodation
    st.markdown("#### Accommodation")
    st.markdown('<div class="budget-item">', unsafe_allow_html=True)
    st.markdown(f"**Hotel Cost:** {format_currency(budget['accommodation'])}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Food
    st.markdown("#### Food & Dining")
    st.markdown('<div class="budget-item">', unsafe_allow_html=True)
    st.markdown(f"**Daily Food Cost:** {format_currency(budget['food'])}")
    st.markdown(f"**Total Food Cost:** {format_currency(budget['food'] * budget['nights'])}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Activities
    st.markdown("#### Activities")
    st.markdown('<div class="budget-item">', unsafe_allow_html=True)
    st.markdown(f"**Daily Activities:** {format_currency(budget['activities'])}")
    st.markdown(f"**Total Activities:** {format_currency(budget['activities'] * budget['nights'])}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Total
    st.markdown('<div class="budget-total">', unsafe_allow_html=True)
    st.markdown(f"**Total Budget:** {format_currency(budget['total'])}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_vehicle_details(fuel_efficiency: float, fuel_price: float, distance: float):
    """Display vehicle details in a structured format."""
    st.markdown("### Vehicle Details")
    
    # Calculate costs
    fuel_required = distance / fuel_efficiency
    fuel_cost = fuel_required * fuel_price
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Fuel Required",
            f"{fuel_required:.1f} liters",
            help="Total fuel needed for the journey"
        )
    with col2:
        st.metric(
            "Fuel Cost",
            format_currency(fuel_cost),
            help="Total cost of fuel for the journey"
        )
    with col3:
        st.metric(
            "Fuel Efficiency",
            f"{fuel_efficiency:.1f} km/l",
            help="Your vehicle's fuel efficiency"
        )
    
    # Additional information
    st.markdown("#### Journey Details")
    st.markdown(f"- **Total Distance:** {distance:.1f} km")
    st.markdown(f"- **Fuel Price:** {format_currency(fuel_price)} per liter")
    st.markdown(f"- **Cost per km:** {format_currency(fuel_cost/distance)}")

def display_hotel_selection(city: str, nights: int) -> Optional[str]:
    """Display hotel selection interface with enhanced styling."""
    hotels_df = get_hotels_in_city(city)
    if hotels_df.empty:
        st.warning(f"No hotels found in {city}")
        return None
    
    # Create hotel options for dropdown
    hotel_options = {
        f"{row['name']} ({row['category']}) - {format_currency(row['price_per_night'])}/night": row['hotel_id']
        for _, row in hotels_df.iterrows()
    }
    
    selected_hotel = st.selectbox(
        "Select a Hotel",
        options=list(hotel_options.keys()),
        format_func=lambda x: x
    )
    
    if selected_hotel:
        hotel_id = hotel_options[selected_hotel]
        hotel_info = hotels_df[hotels_df['hotel_id'] == hotel_id].iloc[0]
        
        # Hotel header with name, rating, and price
        st.markdown(f"### {hotel_info['name']}")
        st.markdown(f'<div class="hotel-rating">⭐ {hotel_info["rating"]}</div>', unsafe_allow_html=True)
        
        # Hotel category and price
        st.markdown(f'<div class="hotel-category">{hotel_info["category"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="hotel-price">Price per night: {format_currency(hotel_info["price_per_night"])}</div>', unsafe_allow_html=True)
        
        # Location and description
        st.markdown(f"**Location:** {hotel_info['location']}")
        st.markdown(f"**Description:** {hotel_info['description']}")
        
        # Amenities
        st.markdown("**Amenities:**")
        amenities = hotel_info['amenities'].split(", ")
        for amenity in amenities:
            st.markdown(f"- {amenity}")
        
        # Total cost
        total_cost = hotel_info['price_per_night'] * nights
        st.markdown(f"**Total Cost for {nights} nights:** {format_currency(total_cost)}")
        
        return hotel_id
    
    return None

def display_transport_details(mode: str, distance: float,
                            fuel_efficiency: Optional[float] = None,
                            fuel_price: float = DEFAULT_FUEL_PRICE):
    """Display transport details based on selected mode."""
    if mode == "vehicle" and fuel_efficiency:
        display_vehicle_details(fuel_efficiency, fuel_price, distance)
    elif mode == "bus":
        st.markdown("### Bus Travel Details")
        st.markdown(f"- **Distance:** {distance:.1f} km")
        st.markdown(f"- **Estimated Travel Time:** {distance/60:.1f} hours")
        st.markdown("- **Note:** Bus ticket prices vary by route and operator")
    elif mode == "flight":
        st.markdown("### Flight Details")
        st.markdown(f"- **Distance:** {distance:.1f} km")
        st.markdown(f"- **Estimated Flight Time:** {distance/800:.1f} hours")
        st.markdown("- **Note:** Flight prices vary by airline and season")

def display_safety_tips(safety: dict):
    """
    Display safety tips in expandable sections.
    
    Args:
        safety (dict): Dictionary containing safety information
    """
    # General Safety Tips
    with st.expander("🔒 General Safety Tips", expanded=True):
        for tip in safety.get("general", []):
            st.markdown(f"• {tip}")
    
    # Emergency Contacts
    with st.expander("🚨 Emergency Contacts", expanded=True):
        emergency = safety.get("emergency", {})
        for service, number in emergency.items():
            st.markdown(f"• **{service.title()}:** {number}")
    
    # Safe Areas
    with st.expander("📍 Safe Areas & Precautions", expanded=True):
        areas = safety.get("areas", {})
        st.markdown("**Safe Areas:**")
        for area in areas.get("safe", []):
            st.markdown(f"• {area}")
        st.markdown("**Areas Requiring Caution:**")
        for area in areas.get("caution", []):
            st.markdown(f"• {area}")
    
    # Transportation Safety
    with st.expander("🚗 Transportation Safety", expanded=True):
        for tip in safety.get("transportation", []):
            st.markdown(f"• {tip}")

def display_attractions(attractions: list[dict]):
    """Render attractions as simple cards."""
    if not attractions:
        st.info("No attractions available.")
        return
    for a in attractions:
        with st.container():
            st.subheader(a["name"])
            st.write(a["description"])
            st.caption(f"{a['category']} • {a['rating']}⭐ • "
                      f"Entry {format_currency(a['entry_fee'])}")
            st.divider()

def display_restaurants(restaurants: list[dict]):
    """Render restaurants as simple cards."""
    if not restaurants:
        st.info("No restaurants available.")
        return
    for r in restaurants:
        with st.container():
            st.subheader(r["name"])
            st.write(f"**Cuisine:** {r['cuisine']}")
            st.write(f"**Specialties:** {', '.join(r['specialties'])}")
            st.caption(f"{r['rating']}⭐ • {r['price_range']}")
            st.divider()

def get_google_maps_route_url(origin: str, destination: str, mode: str = "driving") -> str:
    """Generate Google Maps route URL for the selected cities."""
    # Convert mode to Google Maps travel mode
    travel_mode = {
        "vehicle": "driving",
        "bus": "transit",
        "flight": "driving"  # Google Maps doesn't support flight routes
    }.get(mode, "driving")
    
    # Format cities for URL
    origin_formatted = origin.replace(" ", "+")
    dest_formatted = destination.replace(" ", "+")
    
    # Create Google Maps URL
    return f"https://www.google.com/maps/dir/?api=1&origin={origin_formatted}&destination={dest_formatted}&travelmode={travel_mode}"

def main():
    """Main Streamlit app function."""
    # Title and description
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">✈️ Smart Travel Planner</h1>
            <p style="font-size: 1.1rem; color: #6b7280; max-width: 800px; margin: 0 auto;">
                Plan your perfect trip across Pakistan! Get travel information,
                budget estimates, and discover amazing places to visit.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cities
    cities = load_cities()
    
    # Sidebar with modern styling
    with st.sidebar:
        st.markdown("""
            <div style="padding: 1rem 0;">
                <h2 style="font-size: 1.5rem; margin-bottom: 1.5rem;">Trip Details</h2>
            </div>
        """, unsafe_allow_html=True)
        
        origin = st.selectbox(
            "🚀 Origin City",
            cities,
            index=cities.index("Islamabad") if "Islamabad" in cities else 0
        )
        
        destination = st.selectbox(
            "🎯 Destination City",
            [city for city in cities if city != origin],
            index=0
        )
        
        # Add Google Maps route link after city selection
        if origin and destination:
            maps_url = get_google_maps_route_url(origin, destination)
            st.markdown("---")
            st.markdown("### 🗺️ View Route")
            st.markdown(
                f'<a href="{maps_url}" target="_blank" style="text-decoration: none;">'
                f'<button style="background-color: #4285F4; color: white; padding: 0.5rem 1rem; '
                f'border: none; border-radius: 4px; cursor: pointer; width: 100%;">'
                f'Open in Google Maps</button></a>',
                unsafe_allow_html=True
            )
            st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            nights = st.number_input(
                "🌙 Nights",
                min_value=1,
                max_value=30,
                value=3
            )
        with col2:
            travelers = st.number_input(
                "👥 Travelers",
                min_value=1,
                max_value=10,
                value=2
            )
        
        # Updated travel mode selection
        mode = st.radio(
            "🚗 Travel Mode",
            ["vehicle", "bus", "flight"],
            format_func=lambda x: {
                "vehicle": "🚗 Own Vehicle",
                "bus": "🚌 Local Transport",
                "flight": "✈️ Flight"
            }[x]
        )
        
        # Show vehicle details if own vehicle is selected
        if mode == "vehicle":
            st.markdown("---")
            st.markdown("#### Vehicle Details")
            fuel_efficiency = st.number_input(
                "⛽ Fuel Efficiency (km/liter)",
                min_value=5.0,
                max_value=30.0,
                value=12.0,
                step=0.1,
                help="Enter your vehicle's fuel efficiency in kilometers per liter"
            )
            fuel_price = st.number_input(
                "💰 Fuel Price (PKR/liter)",
                min_value=100.0,
                max_value=500.0,
                value=float(DEFAULT_FUEL_PRICE),
                step=1.0,
                help="Current fuel price per liter"
            )
        else:
            fuel_efficiency = None
            fuel_price = DEFAULT_FUEL_PRICE
        
        # Add hotel selection after destination is chosen
        if destination:
            selected_hotel_id = display_hotel_selection(destination, nights)
        else:
            selected_hotel_id = None
        
        st.markdown("---")
        
        if st.button("Plan Trip ✈️", type="primary", use_container_width=True):
            st.session_state.plan_trip = True
        else:
            st.session_state.plan_trip = False
    
    # Main content area
    if st.session_state.get('plan_trip', False):
        with st.spinner("Planning your perfect trip..."):
            # Calculate route info
            distance = calculate_distance(origin, destination)
            route_info = {
                'km': distance,
                'estimated_hours': distance/60 if mode != "flight" else distance/800
            }
            
            # Estimate budget with selected hotel
            budget = estimate_total_budget(
                origin=origin,
                destination=destination,
                nights=nights,
                travelers=travelers,
                mode=mode,
                fuel_efficiency=fuel_efficiency if mode == "vehicle" else None,
                fuel_price=fuel_price,
                hotel_id=selected_hotel_id
            )
            
            # Add travelers to budget dict for display
            budget["travelers"] = travelers
            
            # Get weather
            weather = get_weather_info(destination)
            
            # Get safety info
            safety = get_all_safety_info(destination)
            
            # Get attractions and restaurants
            attractions = get_top_attractions(destination)
            restaurants = get_top_restaurants(destination)
            
            # Create map
            travel_map = create_travel_map(
                origin=origin,
                destination=destination,
                attractions=attractions,
                restaurants=restaurants
            )
            
            # Display results in a modern layout
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h2 style="font-size: 2rem; margin-bottom: 0.5rem;">Trip to {destination}</h2>
                    <p style="color: #6b7280;">From {origin} • {nights} nights • {travelers} travelers</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Route information in a modern card
            st.subheader("🗺️ Route Information")
            r1, r2, r3 = st.columns(3)
            r1.metric("Distance", f"{route_info['km']:.1f} km")
            r2.metric("Travel Time", f"{route_info['estimated_hours']:.1f} h")
            mode_label = "🚗 Own Vehicle" if mode=="vehicle" else "🚌 Local Transport" if mode=="bus" else "✈️ Flight"
            r3.metric("Mode", mode_label)
            
            # Display transport details based on mode
            display_transport_details(
                mode,
                distance,
                fuel_efficiency if mode == "vehicle" else None,
                fuel_price
            )
            
            # Display weather information
            display_weather_info(destination)
            
            # Display safety tips
            st.markdown("### Safety Tips")
            display_safety_tips(safety)
            
            # Attractions and restaurants in tabs
            tab1, tab2 = st.tabs(["🏛️ Top Attractions", "🍽️ Top Restaurants"])
            with tab1:
                display_attractions(attractions)
            with tab2:
                display_restaurants(restaurants)
            
            # Display budget breakdown
            display_budget_breakdown(budget)
            
            # Interactive map
            folium_static(travel_map, width=1200, height=600)

if __name__ == "__main__":
    main() 