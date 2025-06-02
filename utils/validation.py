"""
Validation utility for the Travel AI system.
"""
from typing import Any, Dict, List, Optional, Union, TypeVar, Type
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
import re
from pathlib import Path
import json

from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(f"{field + ': ' if field else ''}{message}")

class TravelMode(str, Enum):
    """Valid travel modes."""
    DRIVING = "driving"
    WALKING = "walking"
    BICYCLING = "bicycling"
    TRANSIT = "transit"

class AccommodationType(str, Enum):
    """Valid accommodation types."""
    HOTEL = "hotel"
    GUESTHOUSE = "guesthouse"
    HOSTEL = "hostel"
    RESORT = "resort"
    APARTMENT = "apartment"

@dataclass
class ValidationRule:
    """Validation rule definition."""
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[callable] = None

class Validator:
    """Data validator for the application."""
    
    @staticmethod
    def validate_string(value: Any, rule: ValidationRule) -> str:
        """Validate a string value."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        
        if rule.required and not value:
            raise ValidationError("Value is required")
        
        if rule.min_length is not None and len(value) < rule.min_length:
            raise ValidationError(f"Value must be at least {rule.min_length} characters")
        
        if rule.max_length is not None and len(value) > rule.max_length:
            raise ValidationError(f"Value must be at most {rule.max_length} characters")
        
        if rule.pattern and not re.match(rule.pattern, value):
            raise ValidationError(f"Value does not match required pattern: {rule.pattern}")
        
        if rule.allowed_values and value not in rule.allowed_values:
            raise ValidationError(f"Value must be one of: {', '.join(map(str, rule.allowed_values))}")
        
        if rule.custom_validator:
            rule.custom_validator(value)
        
        return value

    @staticmethod
    def validate_number(value: Any, rule: ValidationRule) -> float:
        """Validate a numeric value."""
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            raise ValidationError("Value must be a number")
        
        if rule.min_value is not None and num_value < rule.min_value:
            raise ValidationError(f"Value must be at least {rule.min_value}")
        
        if rule.max_value is not None and num_value > rule.max_value:
            raise ValidationError(f"Value must be at most {rule.max_value}")
        
        if rule.custom_validator:
            rule.custom_validator(num_value)
        
        return num_value

    @staticmethod
    def validate_date(value: Any, rule: ValidationRule) -> date:
        """Validate a date value."""
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD")
        
        if not isinstance(value, (date, datetime)):
            raise ValidationError("Value must be a date")
        
        if rule.custom_validator:
            rule.custom_validator(value)
        
        return value.date() if isinstance(value, datetime) else value

    @staticmethod
    def validate_enum(value: Any, enum_class: Type[Enum]) -> Enum:
        """Validate an enum value."""
        try:
            if isinstance(value, str):
                return enum_class(value)
            elif isinstance(value, enum_class):
                return value
            else:
                raise ValidationError(f"Value must be one of: {', '.join(e.value for e in enum_class)}")
        except ValueError:
            raise ValidationError(f"Invalid value. Must be one of: {', '.join(e.value for e in enum_class)}")

    @staticmethod
    def validate_list(value: Any, item_validator: callable, rule: ValidationRule) -> List:
        """Validate a list of values."""
        if not isinstance(value, list):
            raise ValidationError("Value must be a list")
        
        if rule.required and not value:
            raise ValidationError("List cannot be empty")
        
        if rule.min_length is not None and len(value) < rule.min_length:
            raise ValidationError(f"List must have at least {rule.min_length} items")
        
        if rule.max_length is not None and len(value) > rule.max_length:
            raise ValidationError(f"List must have at most {rule.max_length} items")
        
        return [item_validator(item) for item in value]

    @staticmethod
    def validate_dict(value: Any, schema: Dict[str, ValidationRule]) -> Dict:
        """Validate a dictionary against a schema."""
        if not isinstance(value, dict):
            raise ValidationError("Value must be a dictionary")
        
        result = {}
        for key, rule in schema.items():
            if key not in value:
                if rule.required:
                    raise ValidationError(f"Missing required field: {key}")
                continue
            
            try:
                if isinstance(rule, ValidationRule):
                    if rule.pattern:  # String validation
                        result[key] = Validator.validate_string(value[key], rule)
                    elif rule.min_value is not None or rule.max_value is not None:  # Number validation
                        result[key] = Validator.validate_number(value[key], rule)
                    else:
                        result[key] = value[key]  # Basic validation only
                else:
                    result[key] = rule(value[key])  # Custom validator
            except ValidationError as e:
                e.field = key
                raise
        
        return result

def validate_travel_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a travel request."""
    schema = {
        "origin": ValidationRule(required=True, min_length=2),
        "destination": ValidationRule(required=True, min_length=2),
        "travel_mode": ValidationRule(
            required=True,
            allowed_values=[mode.value for mode in TravelMode]
        ),
        "start_date": ValidationRule(required=True),
        "end_date": ValidationRule(required=True),
        "accommodation_type": ValidationRule(
            required=False,
            allowed_values=[acc.value for acc in AccommodationType]
        ),
        "budget": ValidationRule(required=False, min_value=0),
        "preferences": ValidationRule(required=False)
    }
    
    try:
        # Convert dates
        if "start_date" in data:
            data["start_date"] = Validator.validate_date(data["start_date"], ValidationRule())
        if "end_date" in data:
            data["end_date"] = Validator.validate_date(data["end_date"], ValidationRule())
        
        # Validate travel mode
        if "travel_mode" in data:
            data["travel_mode"] = Validator.validate_enum(data["travel_mode"], TravelMode)
        
        # Validate accommodation type
        if "accommodation_type" in data:
            data["accommodation_type"] = Validator.validate_enum(
                data["accommodation_type"], 
                AccommodationType
            )
        
        # Validate the entire request
        return Validator.validate_dict(data, schema)
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise

def validate_coordinates(lat: float, lon: float) -> tuple[float, float]:
    """Validate geographic coordinates."""
    if not (-90 <= lat <= 90):
        raise ValidationError("Latitude must be between -90 and 90 degrees")
    if not (-180 <= lon <= 180):
        raise ValidationError("Longitude must be between -180 and 180 degrees")
    return lat, lon

def validate_file_path(path: Union[str, Path], required: bool = True) -> Path:
    """Validate a file path."""
    path = Path(path)
    if required and not path.exists():
        raise ValidationError(f"File does not exist: {path}")
    return path

def validate_json_file(path: Union[str, Path], schema: Dict[str, ValidationRule]) -> Dict:
    """Validate a JSON file against a schema."""
    path = validate_file_path(path)
    try:
        with path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        return Validator.validate_dict(data, schema)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON file: {e}")
    except ValidationError as e:
        e.field = str(path)
        raise 