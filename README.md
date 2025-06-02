# 🧳 Smart Travel Planner

A modern travel planning application for Pakistan that helps you plan your perfect trip with interactive maps, budget estimation, and comprehensive travel information.

## Features

- 🗺️ Interactive maps with routes and points of interest
- 💰 Budget estimation for transportation, accommodation, food, and activities
- 🌤️ Weather information (live via OpenWeatherMap API or sample data)
- ⚠️ Safety tips and travel advisories
- 🏛️ Top attractions and restaurants
- 📱 Two interfaces:
  - Streamlit web app (modern, responsive UI)
  - Jupyter notebook (interactive widgets)

## Quick Start

1. Clone this repository:
```bash
git clone https://github.com/yourusername/SmartTravelPlanner.git
cd SmartTravelPlanner
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Streamlit app:
```bash
streamlit run travel_app.py
```

Or open `travel_planner.ipynb` in Jupyter Notebook/Lab.

## Optional: Live Weather Data

For live weather data, set your OpenWeatherMap API key:

1. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
2. Create a `.env` file in the project root:
```
OPENWEATHER_API_KEY=your_api_key_here
```

Without an API key, the app will use sample weather data.

## Project Structure

```
SmartTravelPlanner/
├── data/                  # Sample data files
│   ├── cities.csv        # City coordinates
│   ├── hotels.csv        # Hotel information
│   ├── travel_costs.csv  # Travel costs
│   ├── attractions.csv   # Tourist attractions
│   ├── restaurants.csv   # Restaurant information
│   └── weather_samples.csv
├── images/               # Map images
├── utils/               # Utility modules
│   ├── distance_calculator.py
│   ├── budget_estimator.py
│   ├── weather_fetcher.py
│   ├── safety_info.py
│   ├── places_fetcher.py
│   └── map_utils.py
├── travel_planner.ipynb  # Jupyter interface
├── travel_app.py        # Streamlit interface
└── requirements.txt     # Python dependencies
```

## Usage

### Streamlit App

1. Run `streamlit run travel_app.py`
2. Use the sidebar to input:
   - Origin and destination cities
   - Number of nights
   - Number of travelers
   - Travel mode (road/flight)
3. Click "Plan Trip" to generate your travel plan
4. Explore the results:
   - Route information
   - Budget breakdown
   - Weather forecast
   - Safety tips
   - Top attractions and restaurants
   - Interactive map

### Jupyter Notebook

1. Open `travel_planner.ipynb`
2. Run all cells
3. Use the widgets to input trip details
4. Click "Plan Trip" to generate results
5. View the same information as the Streamlit app

## Data Sources

- City coordinates and distances: Geopy + Nominatim
- Weather data: OpenWeatherMap API (with sample data fallback)
- Hotels, attractions, and restaurants: Sample data
- Safety information: Curated travel tips

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenWeatherMap for weather data
- Folium for interactive maps
- Streamlit for the web interface
- Jupyter for the notebook interface "# SmartTravelPlanner" 
