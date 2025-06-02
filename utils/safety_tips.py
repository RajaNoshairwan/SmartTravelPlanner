"""
Safety tips module for travel planning.

This module provides safety information and tips for travelers in Pakistan.
"""

from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Safety information for major cities
SAFETY_INFO = {
    "Islamabad": {
        "general": [
            "Islamabad is generally considered one of the safest cities in Pakistan",
            "The city has a well-organized grid system and good infrastructure",
            "Most areas are well-lit and patrolled by police"
        ],
        "areas": [
            "Diplomatic Enclave and surrounding areas are highly secure",
            "Blue Area is the main commercial district and generally safe",
            "F-6, F-7, and F-8 sectors are popular residential areas with good security"
        ],
        "transportation": [
            "Use registered taxi services or ride-hailing apps",
            "Public transport is available but can be crowded during peak hours",
            "Metro bus service is safe and reliable"
        ],
        "emergency": {
            "police": "15",
            "ambulance": "1122",
            "fire": "16"
        }
    },
    "Karachi": {
        "general": [
            "Exercise caution in certain areas, especially at night",
            "Stay in well-known areas and hotels",
            "Avoid displaying valuables in public"
        ],
        "areas": [
            "Clifton and Defense Housing Authority (DHA) are generally safe",
            "Saddar area can be crowded; be mindful of your belongings",
            "Avoid isolated areas, especially after dark"
        ],
        "transportation": [
            "Use registered taxi services or ride-hailing apps",
            "Avoid traveling alone at night",
            "Keep car doors locked and windows up in traffic"
        ],
        "emergency": {
            "police": "15",
            "ambulance": "1122",
            "fire": "16"
        }
    },
    "Lahore": {
        "general": [
            "Lahore is generally safe for tourists",
            "The city has a rich cultural heritage and welcoming atmosphere",
            "Most tourist areas are well-patrolled"
        ],
        "areas": [
            "Gulberg and DHA are upscale residential areas with good security",
            "Mall Road and surrounding areas are popular tourist spots",
            "Old City areas can be crowded; be mindful of your belongings"
        ],
        "transportation": [
            "Use registered taxi services or ride-hailing apps",
            "Metro bus service is safe and efficient",
            "Avoid traveling alone at night in less-frequented areas"
        ],
        "emergency": {
            "police": "15",
            "ambulance": "1122",
            "fire": "16"
        }
    },
    "Peshawar": {
        "general": [
            "Exercise caution and stay informed about the current situation",
            "Stay in well-known hotels in central areas",
            "Avoid traveling alone, especially at night"
        ],
        "areas": [
            "University Road area is generally safe",
            "Hayatabad is a modern residential area with good security",
            "Avoid isolated areas and outskirts"
        ],
        "transportation": [
            "Use registered taxi services",
            "Avoid public transport during late hours",
            "Travel in groups when possible"
        ],
        "emergency": {
            "police": "15",
            "ambulance": "1122",
            "fire": "16"
        }
    },
    "Quetta": {
        "general": [
            "Exercise caution and stay informed about the current situation",
            "Stay in well-known hotels in central areas",
            "Avoid traveling alone, especially at night"
        ],
        "areas": [
            "Airport Road area is generally safe",
            "Stay in central areas with good security",
            "Avoid isolated areas and outskirts"
        ],
        "transportation": [
            "Use registered taxi services",
            "Avoid public transport during late hours",
            "Travel in groups when possible"
        ],
        "emergency": {
            "police": "15",
            "ambulance": "1122",
            "fire": "16"
        }
    }
}

def get_safety_tips(city: str) -> Dict[str, List[str]]:
    """
    Get safety tips for a specific city.
    
    Args:
        city (str): Name of the city
        
    Returns:
        Dict[str, List[str]]: Dictionary containing safety information
    """
    try:
        # Get safety info for the city
        city_info = SAFETY_INFO.get(city, SAFETY_INFO["Islamabad"])  # Default to Islamabad if city not found
        
        # Add general travel tips
        general_tips = [
            "Always keep a copy of your important documents",
            "Register with your embassy if staying for an extended period",
            "Keep emergency numbers handy",
            "Be respectful of local customs and traditions",
            "Dress modestly, especially when visiting religious sites",
            "Avoid discussing sensitive political topics",
            "Keep your hotel's address and contact number with you",
            "Use ATMs in well-lit, public areas",
            "Be cautious when using public Wi-Fi",
            "Keep your valuables in the hotel safe"
        ]
        
        # Combine city-specific and general tips
        return {
            "general": general_tips,
            "city_specific": city_info["general"],
            "areas": city_info["areas"],
            "transportation": city_info["transportation"],
            "emergency": city_info["emergency"]
        }
        
    except Exception as e:
        logger.error(f"Error getting safety tips for {city}: {e}")
        return {
            "general": ["Exercise caution and stay informed about the current situation"],
            "city_specific": ["No specific information available"],
            "areas": ["Stay in well-known areas"],
            "transportation": ["Use registered taxi services"],
            "emergency": {"police": "15", "ambulance": "1122", "fire": "16"}
        } 