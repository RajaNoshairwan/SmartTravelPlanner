"""
API client utility for the Travel AI system.
"""
from typing import Any, Dict, List, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
from datetime import datetime
import time
from pathlib import Path

from config import API_KEYS
from utils.logger import get_logger, api_logger
from utils.cache import cached
from utils.validation import validate_coordinates, ValidationError

logger = get_logger(__name__)

class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(f"{message} (Status: {status_code})" if status_code else message)

class APIClient:
    """Base API client with common functionality."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: int = 30
    ) -> Dict:
        """Make an API request with error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Add API key to params if available
        if self.api_key:
            params = params or {}
            params['api_key'] = self.api_key
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=headers,
                timeout=timeout
            )
            
            # Raise for bad status codes
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', None)
            try:
                error_data = e.response.json() if e.response else None
            except:
                error_data = None
            
            raise APIError(
                f"API request failed: {str(e)}",
                status_code=status_code,
                response=error_data
            )

class WeatherAPI(APIClient):
    """Client for OpenWeather API."""
    
    def __init__(self):
        super().__init__(
            base_url="https://api.openweathermap.org/data/2.5",
            api_key=API_KEYS["OPENWEATHER"]
        )
    
    @api_logger("OpenWeather")
    @cached(ttl=1800)  # Cache for 30 minutes
    def get_weather(self, city: str) -> Dict:
        """Get current weather for a city."""
        return self._make_request(
            method="GET",
            endpoint="/weather",
            params={
                "q": city,
                "units": "metric",
                "appid": self.api_key
            }
        )
    
    @api_logger("OpenWeather")
    @cached(ttl=3600)  # Cache for 1 hour
    def get_forecast(self, city: str) -> Dict:
        """Get 5-day weather forecast for a city."""
        return self._make_request(
            method="GET",
            endpoint="/forecast",
            params={
                "q": city,
                "units": "metric",
                "appid": self.api_key
            }
        )

class MapsAPI(APIClient):
    """Client for Google Maps API."""
    
    def __init__(self):
        super().__init__(
            base_url="https://maps.googleapis.com/maps/api",
            api_key=API_KEYS["GOOGLE_MAPS"]
        )
    
    @api_logger("GoogleMaps")
    @cached(ttl=86400)  # Cache for 24 hours
    def get_geocode(self, address: str) -> Dict:
        """Get geocoding information for an address."""
        return self._make_request(
            method="GET",
            endpoint="/geocode/json",
            params={"address": address}
        )
    
    @api_logger("GoogleMaps")
    @cached(ttl=3600)  # Cache for 1 hour
    def get_directions(
        self,
        origin: str,
        destination: str,
        mode: str = "driving",
        waypoints: Optional[List[str]] = None
    ) -> Dict:
        """Get directions between two locations."""
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode
        }
        
        if waypoints:
            params["waypoints"] = "|".join(waypoints)
        
        return self._make_request(
            method="GET",
            endpoint="/directions/json",
            params=params
        )
    
    @api_logger("GoogleMaps")
    @cached(ttl=86400)  # Cache for 24 hours
    def get_places(
        self,
        location: tuple[float, float],
        radius: int = 5000,
        type: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> Dict:
        """Search for places near a location."""
        try:
            lat, lng = validate_coordinates(*location)
        except ValidationError as e:
            raise APIError(f"Invalid coordinates: {e}")
        
        params = {
            "location": f"{lat},{lng}",
            "radius": radius
        }
        
        if type:
            params["type"] = type
        if keyword:
            params["keyword"] = keyword
        
        return self._make_request(
            method="GET",
            endpoint="/place/nearbysearch/json",
            params=params
        )

class HotelsAPI(APIClient):
    """Client for Hotels.com API."""
    
    def __init__(self):
        super().__init__(
            base_url="https://hotels.com/api/v2",
            api_key=API_KEYS["HOTELS_API"]
        )
    
    @api_logger("Hotels")
    @cached(ttl=3600)  # Cache for 1 hour
    def search_hotels(
        self,
        location: str,
        check_in: datetime,
        check_out: datetime,
        guests: int = 1,
        rooms: int = 1
    ) -> Dict:
        """Search for hotels in a location."""
        return self._make_request(
            method="GET",
            endpoint="/hotels/search",
            params={
                "location": location,
                "check_in": check_in.strftime("%Y-%m-%d"),
                "check_out": check_out.strftime("%Y-%m-%d"),
                "guests": guests,
                "rooms": rooms
            }
        )
    
    @api_logger("Hotels")
    @cached(ttl=3600)  # Cache for 1 hour
    def get_hotel_details(self, hotel_id: str) -> Dict:
        """Get detailed information about a hotel."""
        return self._make_request(
            method="GET",
            endpoint=f"/hotels/{hotel_id}"
        )

# Create global API client instances
weather_api = WeatherAPI()
maps_api = MapsAPI()
hotels_api = HotelsAPI()

def get_api_client(api_name: str) -> APIClient:
    """Get an API client instance by name."""
    clients = {
        "weather": weather_api,
        "maps": maps_api,
        "hotels": hotels_api
    }
    
    if api_name not in clients:
        raise ValueError(f"Unknown API client: {api_name}")
    
    return clients[api_name] 