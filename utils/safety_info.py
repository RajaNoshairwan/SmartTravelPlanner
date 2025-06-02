"""
Safety info module for travel planning.

This module provides safety information and tips for travelers in Pakistan.
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
SAFETY_CSV = DATA_DIR / "safety_info.csv"

# Default safety information if CSV is not available
DEFAULT_SAFETY_INFO = {
    "Islamabad": {
        "general": [
            "Islamabad is generally considered one of the safest cities in Pakistan",
            "The city has a well-organized grid system and good infrastructure",
            "Most areas are well-lit and patrolled by police"
        ],
        "emergency": {
            "police": "15",
            "ambulance": "1122",
            "fire": "16",
            "tourist_police": "051-9258552"
        },
        "areas": {
            "safe": [
                "Diplomatic Enclave",
                "Blue Area",
                "F-6, F-7, and F-8 sectors",
                "G-6, G-7, and G-8 sectors"
            ],
            "caution": [
                "Peripheral areas after dark",
                "Less populated sectors at night"
            ]
        },
        "transportation": [
            "Use registered taxi services or ride-hailing apps",
            "Public transport is available but can be crowded during peak hours",
            "Metro bus service is safe and reliable",
            "Keep car doors locked and windows up in traffic"
        ]
    },
    "Lahore": {
        "general": [
            "Lahore is generally safe for tourists",
            "The city has a rich cultural heritage and welcoming atmosphere",
            "Most tourist areas are well-patrolled"
        ],
        "emergency": {
            "police": "15",
            "ambulance": "1122",
            "fire": "16",
            "tourist_police": "042-99230444"
        },
        "areas": {
            "safe": [
                "Gulberg",
                "DHA",
                "Mall Road",
                "Fortress Stadium area"
            ],
            "caution": [
                "Old City areas at night",
                "Less frequented areas after dark"
            ]
        },
        "transportation": [
            "Use registered taxi services or ride-hailing apps",
            "Metro bus service is safe and efficient",
            "Avoid traveling alone at night in less-frequented areas",
            "Keep car doors locked and windows up in traffic"
        ]
    },
    "Karachi": {
        "general": [
            "Exercise caution in certain areas, especially at night",
            "Stay in well-known areas and hotels",
            "Avoid displaying valuables in public"
        ],
        "emergency": {
            "police": "15",
            "ambulance": "1122",
            "fire": "16",
            "tourist_police": "021-99212626"
        },
        "areas": {
            "safe": [
                "Clifton",
                "DHA",
                "Gulshan-e-Iqbal",
                "Defence Housing Authority"
            ],
            "caution": [
                "Saddar area at night",
                "Peripheral areas",
                "Less frequented neighborhoods"
            ]
        },
        "transportation": [
            "Use registered taxi services or ride-hailing apps",
            "Avoid public transport during late hours",
            "Keep car doors locked and windows up in traffic",
            "Travel in groups when possible"
        ]
    }
}

def load_safety_data() -> Dict:
    """Load safety information from CSV or use default data."""
    try:
        if SAFETY_CSV.exists():
            df = pd.read_csv(SAFETY_CSV)
            safety_info = {}
            for city in df['city'].unique():
                city_data = df[df['city'] == city]
                safety_info[city] = {
                    "general": city_data['general'].tolist(),
                    "emergency": eval(city_data['emergency'].iloc[0]),
                    "areas": eval(city_data['areas'].iloc[0]),
                    "transportation": city_data['transportation'].tolist()
                }
            return safety_info
        return DEFAULT_SAFETY_INFO
    except Exception as e:
        logger.error(f"Error loading safety data: {e}")
        return DEFAULT_SAFETY_INFO

def get_all_safety_info(city: str) -> Dict:
    """
    Get comprehensive safety information for a city.
    
    Args:
        city (str): Name of the city
        
    Returns:
        Dict: Dictionary containing safety information
    """
    try:
        safety_data = load_safety_data()
        return safety_data.get(city, safety_data["Islamabad"])
    except Exception as e:
        logger.error(f"Error getting safety info for {city}: {e}")
        return {
            "general": ["Exercise caution and stay informed about the current situation"],
            "emergency": {"police": "15", "ambulance": "1122", "fire": "16"},
            "areas": {"safe": ["Stay in well-known areas"], "caution": ["Avoid isolated areas"]},
            "transportation": ["Use registered taxi services"]
        }

def get_emergency_numbers(city: str) -> Dict[str, str]:
    """
    Get emergency contact numbers for a city.
    
    Args:
        city (str): Name of the city
        
    Returns:
        Dict[str, str]: Dictionary of emergency contact numbers
    """
    try:
        safety_info = get_all_safety_info(city)
        return safety_info.get("emergency", {
            "police": "15",
            "ambulance": "1122",
            "fire": "16"
        })
    except Exception as e:
        logger.error(f"Error getting emergency numbers for {city}: {e}")
        return {
            "police": "15",
            "ambulance": "1122",
            "fire": "16"
        }

def get_safe_areas(city: str) -> Dict[str, List[str]]:
    """
    Get information about safe and caution areas in a city.
    
    Args:
        city (str): Name of the city
        
    Returns:
        Dict[str, List[str]]: Dictionary containing safe and caution areas
    """
    try:
        safety_info = get_all_safety_info(city)
        return safety_info.get("areas", {
            "safe": ["Stay in well-known areas"],
            "caution": ["Avoid isolated areas"]
        })
    except Exception as e:
        logger.error(f"Error getting safe areas for {city}: {e}")
        return {
            "safe": ["Stay in well-known areas"],
            "caution": ["Avoid isolated areas"]
        }

def get_transportation_safety(city: str) -> List[str]:
    """
    Get transportation safety tips for a city.
    
    Args:
        city (str): Name of the city
        
    Returns:
        List[str]: List of transportation safety tips
    """
    try:
        safety_info = get_all_safety_info(city)
        return safety_info.get("transportation", ["Use registered taxi services"])
    except Exception as e:
        logger.error(f"Error getting transportation safety for {city}: {e}")
        return ["Use registered taxi services"] 