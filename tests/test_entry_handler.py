import pytest
import json
from unittest.mock import patch, Mock

from src.handlers.entry import lambda_handler

# AI generated tests
class TestEntryHandler:
    """Test cases for entry Lambda handler."""

    def test_successful_entry(self):
        """Test successful parking entry creation."""
        event = {
            'queryStringParameters': {
                'plate': 'ABC123',
                'parkingLot': '1'
            }
        }
        context = {}
        
        with patch('src.handlers.entry.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.create_entry.return_value = 'test-ticket-id'
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['ticketId'] == 'test-ticket-id'
        mock_service.create_entry.assert_called_once_with('ABC123', 1)

    def test_missing_plate_parameter(self):
        """Test entry with missing plate parameter."""
        event = {
            'queryStringParameters': {
                'parkingLot': '1'
            }
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'License plate is required' in body['error']

    def test_missing_parking_lot_parameter(self):
        """Test entry with missing parking lot parameter."""
        event = {
            'queryStringParameters': {
                'plate': 'ABC123'
            }
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Parking lot is required' in body['error']

    def test_invalid_plate_format(self):
        """Test entry with invalid plate format."""
        event = {
            'queryStringParameters': {
                'plate': '',
                'parkingLot': '1'
            }
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'License plate is required' in body['error']

    def test_invalid_parking_lot_format(self):
        """Test entry with invalid parking lot format."""
        event = {
            'queryStringParameters': {
                'plate': 'ABC123',
                'parkingLot': 'invalid'
            }
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Parking lot must be a valid integer' in body['error']

    def test_parking_lot_out_of_range(self):
        """Test entry with parking lot number out of range."""
        event = {
            'queryStringParameters': {
                'plate': 'ABC123',
                'parkingLot': '10000'
            }
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Parking lot must be between 1 and 9999' in body['error']

    def test_null_query_parameters(self):
        """Test entry with null query parameters (API Gateway behavior)."""
        event = {
            'queryStringParameters': None
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'License plate is required' in body['error']

    def test_empty_query_parameters(self):
        """Test entry with empty query parameters."""
        event = {
            'queryStringParameters': {}
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400

    def test_service_exception(self):
        """Test entry handler with service exception."""
        event = {
            'queryStringParameters': {
                'plate': 'ABC123',
                'parkingLot': '1'
            }
        }
        context = {}
        
        with patch('src.handlers.entry.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.create_entry.side_effect = Exception("Database error")
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Failed to create parking entry' in body['error']

    def test_plate_normalization(self):
        """Test that license plate is normalized (uppercase, trimmed)."""
        event = {
            'queryStringParameters': {
                'plate': '  abc123  ',
                'parkingLot': '1'
            }
        }
        context = {}
        
        with patch('src.handlers.entry.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.create_entry.return_value = 'test-ticket-id'
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 201
        # Should be called with normalized plate
        mock_service.create_entry.assert_called_once_with('ABC123', 1)

    def test_cors_headers(self):
        """Test that CORS headers are included in response."""
        event = {
            'queryStringParameters': {
                'plate': 'ABC123',
                'parkingLot': '1'
            }
        }
        context = {}
        
        with patch('src.handlers.entry.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.create_entry.return_value = 'test-ticket-id'
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        headers = response['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Content-Type'] == 'application/json' 