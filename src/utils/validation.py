import re
from typing import Dict, Any, Optional, Tuple


def validate_license_plate(plate: str) -> Tuple[bool, Optional[str]]:
    """
    Validate license plate format.
    
    Args:
        plate: License plate string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not plate or not isinstance(plate, str):
        return False, "License plate is required and must be a string"
    
    plate = plate.strip()
    
    if len(plate) < 2 or len(plate) > 15:
        return False, "License plate must be between 2 and 15 characters"
    
    # Allow alphanumeric characters, spaces, and hyphens
    if not re.match(r'^[A-Za-z0-9\s\-]+$', plate):
        return False, "License plate contains invalid characters"
    
    return True, None


def validate_parking_lot(parking_lot: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate parking lot identifier.
    
    Args:
        parking_lot: Parking lot value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if parking_lot is None or parking_lot == '':
        return False, "Parking lot is required"
    
    try:
        lot_int = int(parking_lot)
        if lot_int < 1 or lot_int > 9999:
            return False, "Parking lot must be between 1 and 9999"
        return True, None
    except (ValueError, TypeError):
        return False, "Parking lot must be a valid integer"


def validate_ticket_id(ticket_id: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate ticket ID format.
    
    Args:
        ticket_id: Ticket ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ticket_id or not isinstance(ticket_id, str):
        return False, "Ticket ID is required and must be a string"
    
    ticket_id = ticket_id.strip()
    
    # Basic UUID format validation
    if not re.match(r'^[a-f0-9\-]{36}$', ticket_id.lower()):
        return False, "Invalid ticket ID format"
    
    return True, None


def extract_query_params(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract and normalize query parameters from Lambda event.
    
    Args:
        event: Lambda event dictionary
        
    Returns:
        Dictionary of query parameters
    """
    query_params = event.get('queryStringParameters') or {}
    
    # Handle null case from API Gateway
    if query_params is None:
        return {}
    
    # Normalize to empty strings if None values
    return {k: v or '' for k, v in query_params.items()} 