import json
import nbformat as nbf

# Create a new notebook
nb = nbf.v4.new_notebook()

# Add markdown cell for introduction
intro_cell = nbf.v4.new_markdown_cell("""# Smart Travel Planner - Pakistan

This notebook provides an interactive interface for planning trips across Pakistan. You can:
- Calculate distances and travel times between cities
- Estimate travel costs based on different transportation modes
- Get weather information for your destination
- View safety tips and recommendations
- Discover top attractions and restaurants
- Select hotels and calculate accommodation costs
- View interactive maps of your route

## Requirements
Make sure you have installed all required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

Also, ensure you have set your OpenWeatherMap API key for live weather data.""")

# Add code cell for imports
imports_cell = nbf.v4.new_code_cell("""# Import required libraries
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from typing import Dict, List, Optional
import os
from datetime import datetime, timedelta

# Import utility modules
from utils.distance_calculator import calculate_distance, get_cities
from utils.budget_estimator import (
    estimate_total_budget, get_hotels_in_city, get_hotel_cost_by_id,
    DEFAULT_FUEL_PRICE
)
from utils.weather_fetcher import get_weather_info
from utils.safety_info import get_safety_tips
from utils.places_fetcher import get_attractions, get_restaurants
from utils.map_utils import create_route_map

# Set OpenWeather API key
os.environ["OPENWEATHER_API_KEY"] = "ad9dd2f3e0d38465e08d5b29708471bc"

# Load cities data
cities_df = get_cities()""")

# Add code cell for utility functions
utils_cell = nbf.v4.new_code_cell("""def format_currency(amount: float) -> str:
    \"\"\"Format amount as currency string\"\"\"
    return f"Rs. {amount:,.2f}"

def display_weather_info(city: str):
    \"\"\"Display weather information for a city\"\"\"
    weather_info = get_weather_info(city)
    if weather_info:
        st.write(f"### Current Weather in {city}")
        st.write(f"Temperature: {weather_info['temperature']}°C")
        st.write(f"Condition: {weather_info['condition']}")
        st.write(f"Humidity: {weather_info['humidity']}%")
        st.write(f"Wind Speed: {weather_info['wind_speed']} km/h")
    else:
        st.warning(f"Could not fetch weather data for {city}")

def display_safety_tips(city: str):
    \"\"\"Display safety tips for a city\"\"\"
    tips = get_safety_tips(city)
    if tips:
        st.write("### Safety Tips")
        for tip in tips:
            st.write(f"- {tip}")
    else:
        st.info(f"No specific safety tips available for {city}")

def display_hotel_selection(city: str, nights: int) -> Optional[str]:
    \"\"\"Display hotel selection interface and return selected hotel ID\"\"\"
    hotels_df = get_hotels_in_city(city)
    
    if hotels_df.empty:
        st.warning(f"No hotels found in {city}")
        return None
    
    # Create hotel selection dropdown
    hotel_options = {f"{row['name']} (Rs. {row['price_per_night']:,.2f}/night)": row['id'] 
                    for _, row in hotels_df.iterrows()}
    selected_hotel = st.selectbox("Select a Hotel", list(hotel_options.keys()))
    
    if selected_hotel:
        hotel_id = hotel_options[selected_hotel]
        hotel_info = hotels_df[hotels_df['id'] == hotel_id].iloc[0]
        
        # Display hotel details
        st.write("### Hotel Details")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {hotel_info['name']}")
            st.write(f"**Rating:** {hotel_info['rating']} ⭐")
            st.write(f"**Price per night:** {format_currency(hotel_info['price_per_night'])}")
        with col2:
            st.write(f"**Location:** {hotel_info['location']}")
            st.write(f"**Total for {nights} nights:** {format_currency(hotel_info['price_per_night'] * nights)}")
        
        st.write("**Description:**")
        st.write(hotel_info['description'])
        
        return hotel_id
    return None""")

# Add code cell for main interface
main_cell = nbf.v4.new_code_cell("""# Create the main interface
st.title("Smart Travel Planner - Pakistan")

# Sidebar for inputs
st.sidebar.header("Trip Details")

# Origin city selection
origin = st.sidebar.selectbox(
    "Origin City",
    cities_df['city'].tolist(),
    index=cities_df[cities_df['city'] == 'Islamabad'].index[0] if 'Islamabad' in cities_df['city'].values else 0
)

# Destination city selection
destination = st.sidebar.selectbox(
    "Destination City",
    cities_df['city'].tolist(),
    index=cities_df[cities_df['city'] == 'Lahore'].index[0] if 'Lahore' in cities_df['city'].values else 1
)

# Number of nights
nights = st.sidebar.number_input("Number of Nights", min_value=1, max_value=30, value=3)

# Number of travelers
travelers = st.sidebar.number_input("Number of Travelers", min_value=1, max_value=10, value=2)

# Travel mode selection
travel_mode = st.sidebar.radio(
    "Travel Mode",
    ["vehicle", "bus", "flight"],
    format_func=lambda x: {
        "vehicle": "Own Vehicle",
        "bus": "Local Transport",
        "flight": "Flight"
    }[x]
)

# Vehicle details (if own vehicle selected)
fuel_efficiency = None
fuel_price = None
if travel_mode == "vehicle":
    st.sidebar.subheader("Vehicle Details")
    fuel_efficiency = st.sidebar.number_input(
        "Fuel Efficiency (km/liter)",
        min_value=5.0,
        max_value=30.0,
        value=12.0,
        help="Enter your vehicle's fuel efficiency in kilometers per liter"
    )
    fuel_price = st.sidebar.number_input(
        "Fuel Price (Rs/liter)",
        min_value=50.0,
        max_value=500.0,
        value=DEFAULT_FUEL_PRICE,
        help="Current fuel price per liter"
    )

# Calculate distance and time
distance = calculate_distance(origin, destination)
if distance:
    st.sidebar.metric("Distance", f"{distance['distance']:.1f} km")
    st.sidebar.metric("Estimated Travel Time", f"{distance['time']:.1f} hours")

# Main content area
if origin and destination:
    # Calculate budget
    budget = estimate_total_budget(
        origin=origin,
        destination=destination,
        nights=nights,
        travelers=travelers,
        travel_mode=travel_mode,
        fuel_efficiency=fuel_efficiency,
        fuel_price=fuel_price
    )
    
    if budget:
        # Display budget breakdown
        st.header("Budget Estimate")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cost", format_currency(budget['total_cost']))
        with col2:
            st.metric("Per Person", format_currency(budget['total_cost'] / travelers))
        with col3:
            st.metric("Per Day", format_currency(budget['total_cost'] / nights))
        
        # Display cost breakdown
        st.subheader("Cost Breakdown")
        cost_col1, cost_col2 = st.columns(2)
        with cost_col1:
            st.write("**Transportation:**")
            st.write(f"- {format_currency(budget['transportation_cost'])}")
            if travel_mode == "vehicle":
                st.write(f"  (Fuel cost: {format_currency(budget['transportation_cost'])})")
            elif travel_mode == "bus":
                st.write(f"  (Bus tickets: {format_currency(budget['transportation_cost'] / travelers)} per person)")
            elif travel_mode == "flight":
                st.write(f"  (Flight tickets: {format_currency(budget['transportation_cost'] / travelers)} per person)")
        
        with cost_col2:
            st.write("**Accommodation:**")
            st.write(f"- {format_currency(budget['accommodation_cost'])}")
            st.write(f"  ({format_currency(budget['accommodation_cost'] / nights)} per night)")
        
        st.write("**Food & Activities:**")
        st.write(f"- Food: {format_currency(budget['food_cost'])}")
        st.write(f"- Activities: {format_currency(budget['activities_cost'])}")
    
    # Display route map
    st.header("Route Map")
    route_map = create_route_map(origin, destination)
    if route_map:
        folium_static(route_map)
    
    # Display weather information
    display_weather_info(destination)
    
    # Display safety tips
    display_safety_tips(destination)
    
    # Display attractions and restaurants
    st.header("Places to Visit")
    attractions = get_attractions(destination)
    if attractions:
        st.subheader("Top Attractions")
        for attraction in attractions:
            st.write(f"**{attraction['name']}**")
            st.write(f"Rating: {attraction['rating']} ⭐")
            st.write(f"Type: {attraction['type']}")
            st.write(f"Description: {attraction['description']}")
            st.write("---")
    
    st.header("Restaurants")
    restaurants = get_restaurants(destination)
    if restaurants:
        for restaurant in restaurants:
            st.write(f"**{restaurant['name']}**")
            st.write(f"Rating: {restaurant['rating']} ⭐")
            st.write(f"Cuisine: {restaurant['cuisine']}")
            st.write(f"Price Range: {restaurant['price_range']}")
            st.write(f"Description: {restaurant['description']}")
            st.write("---")""")

# Add all cells to the notebook
nb.cells = [intro_cell, imports_cell, utils_cell, main_cell]

# Write the notebook to a file
with open('travel_planner.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)""")

# Run the script to create the notebook
import subprocess
subprocess.run(['python', 'create_notebook.py'])

# Clean up the script
import os
os.remove('create_notebook.py') 