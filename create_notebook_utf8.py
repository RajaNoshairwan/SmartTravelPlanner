import json
import nbformat as nbf

def create_notebook():
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
    
    # Add all cells to the notebook
    nb.cells = [intro_cell, imports_cell]
    
    # Convert notebook to JSON with proper encoding
    notebook_json = nbf.writes(nb)
    
    # Write to file with UTF-8 encoding
    with open('travel_planner.ipynb', 'w', encoding='utf-8') as f:
        f.write(notebook_json)

if __name__ == '__main__':
    create_notebook() 