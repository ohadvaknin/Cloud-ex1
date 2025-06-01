import logging
from typing import Dict, Any

from services.parking_service import ParkingService
from utils.response import success_response, validation_error_response, not_found_response, internal_error_response
from utils.validation import validate_ticket_id, extract_query_params

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for parking exit endpoint.
    
    Expected: POST /exit?ticketId=<string>
    Returns: { "plate": "<string>", "totalTimeMinutes": <int>, "parkingLot": <int>, "chargeUSD": <float> }
    """
    logger.info(f"Exit request: {event}")
    
    try:
        # Extract query parameters
        params = extract_query_params(event)
        ticket_id = params.get('ticketId', '').strip()
        
        # Validate ticket ID
        ticket_valid, ticket_error = validate_ticket_id(ticket_id)
        if not ticket_valid:
            logger.warning(f"Invalid ticket ID validation: {ticket_error}")
            return validation_error_response(ticket_error)
        
        # Process parking exit
        parking_service = ParkingService()
        exit_info = parking_service.process_exit(ticket_id)
        
        logger.info(f"Processed parking exit: {exit_info}")
        
        return success_response(exit_info)
        
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Business logic error: {error_msg}")
        
        # Check if it's a not found error
        if "not found" in error_msg.lower():
            return not_found_response(error_msg)
        else:
            return validation_error_response(error_msg)
    
    except Exception as e:
        logger.error(f"Internal error in exit handler: {str(e)}")
        return internal_error_response("Failed to process parking exit") 