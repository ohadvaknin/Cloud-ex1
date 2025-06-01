import json
from typing import Any, Dict, Optional


def create_response(
    status_code: int,
    body: Any,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Create standardized Lambda response.
    
    Args:
        status_code: HTTP status code
        body: Response body (will be JSON serialized)
        headers: Optional HTTP headers
        
    Returns:
        Lambda response dictionary
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, default=str)
    }


def success_response(body: Any, status_code: int = 200) -> Dict[str, Any]:
    """Create success response."""
    return create_response(status_code, body)


def error_response(message: str, status_code: int = 500, error_code: Optional[str] = None) -> Dict[str, Any]:
    """Create error response."""
    error_body = {
        'error': message,
        'statusCode': status_code
    }
    
    if error_code:
        error_body['errorCode'] = error_code
    
    return create_response(status_code, error_body)


def validation_error_response(message: str) -> Dict[str, Any]:
    """Create validation error response."""
    return error_response(message, 400, 'VALIDATION_ERROR')


def not_found_response(message: str = "Resource not found") -> Dict[str, Any]:
    """Create not found error response."""
    return error_response(message, 404, 'NOT_FOUND')


def internal_error_response(message: str = "Internal server error") -> Dict[str, Any]:
    """Create internal server error response."""
    return error_response(message, 500, 'INTERNAL_ERROR') 