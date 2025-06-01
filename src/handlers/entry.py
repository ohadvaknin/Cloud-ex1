import logging
from typing import Dict, Any

from services.parking_service import ParkingService
from utils.response import success_response, validation_error_response, internal_error_response
from utils.validation import validate_license_plate, validate_parking_lot, extract_query_params

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for parking entry endpoint.
    
    Expected: POST /entry?plate=<string>&parkingLot=<int>
    Returns: { "ticketId": "<uuid>" }
    """
    logger.info(f"Entry request: {event}")
    
    try:
        # Extract query parameters
        params = extract_query_params(event)
        plate = params.get('plate', '').strip().upper()
        parking_lot_str = params.get('parkingLot', '')
        
        # Validate license plate
        plate_valid, plate_error = validate_license_plate(plate)
        if not plate_valid:
            logger.warning(f"Invalid plate validation: {plate_error}")
            return validation_error_response(plate_error)
        
        # Validate parking lot
        lot_valid, lot_error = validate_parking_lot(parking_lot_str)
        if not lot_valid:
            logger.warning(f"Invalid parking lot validation: {lot_error}")
            return validation_error_response(lot_error)
        
        parking_lot = int(parking_lot_str)
        
        # Create parking entry
        parking_service = ParkingService()
        ticket_id = parking_service.create_entry(plate, parking_lot)
        
        logger.info(f"Created parking entry: ticket_id={ticket_id}, plate={plate}, lot={parking_lot}")
        
        return success_response({
            'ticketId': ticket_id
        }, 201)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return validation_error_response(str(e))
    
    except Exception as e:
        logger.error(f"Internal error in entry handler: {str(e)}")
        return internal_error_response("Failed to create parking entry") 