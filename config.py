"""
Configuration management for the Travel AI system.
"""
from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / "cache"
LOGS_DIR = BASE_DIR / "logs"

# Create necessary directories
for directory in [DATA_DIR, CACHE_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# API Keys and External Services
API_KEYS = {
    "OPENWEATHER": os.getenv("OPENWEATHER_API_KEY"),
    "GOOGLE_MAPS": os.getenv("GOOGLE_MAPS_API_KEY"),
    "HOTELS_API": os.getenv("HOTELS_API_KEY"),
}

# Application Settings
APP_CONFIG = {
    "name": "Smart Travel Planner",
    "version": "2.0.0",
    "description": "AI-powered travel planning system for Pakistan",
    "debug": os.getenv("DEBUG", "False").lower() == "true",
    "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),  # Cache time in seconds
}

# Data Files
DATA_FILES = {
    "cities": DATA_DIR / "cities.csv",
    "hotels": DATA_DIR / "hotels.json",
    "attractions": DATA_DIR / "attractions.json",
    "restaurants": DATA_DIR / "restaurants.json",
}

# Default Values
DEFAULTS = {
    "fuel_price": float(os.getenv("DEFAULT_FUEL_PRICE", "250.0")),
    "currency": "PKR",
    "language": "en",
    "max_results": 10,
    "default_radius": 5000,  # meters
}

# Cache Settings
CACHE_CONFIG = {
    "enabled": True,
    "type": "file",  # or 'memory'
    "ttl": APP_CONFIG["cache_ttl"],
    "max_size": 1000,  # maximum number of cached items
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "app.log",
            "formatter": "standard",
            "level": "INFO",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True
        }
    }
}

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary."""
    return {
        "base_dir": BASE_DIR,
        "data_dir": DATA_DIR,
        "cache_dir": CACHE_DIR,
        "logs_dir": LOGS_DIR,
        "api_keys": API_KEYS,
        "app_config": APP_CONFIG,
        "data_files": DATA_FILES,
        "defaults": DEFAULTS,
        "cache_config": CACHE_CONFIG,
        "logging_config": LOGGING_CONFIG,
    }

def validate_config() -> bool:
    """Validate the configuration settings."""
    try:
        # Check if required API keys are present
        required_keys = ["OPENWEATHER"]
        missing_keys = [key for key in required_keys if not API_KEYS.get(key)]
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")

        # Validate data files exist
        for file_path in DATA_FILES.values():
            if not file_path.exists():
                raise FileNotFoundError(f"Required data file not found: {file_path}")

        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False 