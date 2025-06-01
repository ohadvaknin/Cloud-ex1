import pytest
import json
from unittest.mock import patch, Mock

from src.handlers.exit import lambda_handler

# AI generated tests
class TestExitHandler:
    """Test cases for exit Lambda handler."""

    def test_successful_exit(self):
        """Test successful parking exit processing."""
        event = {
            'queryStringParameters': {
                'ticketId': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
            }
        }
        context = {}
        
        expected_exit_info = {
            'plate': 'ABC123',
            'totalTimeMinutes': 45,
            'parkingLot': 1,
            'chargeUSD': 7.50
        }
        
        with patch('src.handlers.exit.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.process_exit.return_value = expected_exit_info
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body == expected_exit_info
        mock_service.process_exit.assert_called_once_with('a1b2c3d4-e5f6-7890-abcd-ef1234567890')

    def test_missing_ticket_id_parameter(self):
        """Test exit with missing ticket ID parameter."""
        event = {
            'queryStringParameters': {}
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Ticket ID is required' in body['error']

    def test_invalid_ticket_id_format(self):
        """Test exit with invalid ticket ID format."""
        event = {
            'queryStringParameters': {
                'ticketId': 'invalid-ticket-id'
            }
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Invalid ticket ID format' in body['error']

    def test_empty_ticket_id(self):
        """Test exit with empty ticket ID."""
        event = {
            'queryStringParameters': {
                'ticketId': ''
            }
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Ticket ID is required' in body['error']

    def test_ticket_not_found(self):
        """Test exit with non-existent ticket."""
        event = {
            'queryStringParameters': {
                'ticketId': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
            }
        }
        context = {}
        
        with patch('src.handlers.exit.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.process_exit.side_effect = ValueError("Ticket a1b2c3d4-e5f6-7890-abcd-ef1234567890 not found")
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'not found' in body['error']

    def test_ticket_already_processed(self):
        """Test exit with already processed ticket."""
        event = {
            'queryStringParameters': {
                'ticketId': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
            }
        }
        context = {}
        
        with patch('src.handlers.exit.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.process_exit.side_effect = ValueError("Ticket a1b2c3d4-e5f6-7890-abcd-ef1234567890 already processed")
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'already processed' in body['error']

    def test_null_query_parameters(self):
        """Test exit with null query parameters (API Gateway behavior)."""
        event = {
            'queryStringParameters': None
        }
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'Ticket ID is required' in body['error']

    def test_service_exception(self):
        """Test exit handler with service exception."""
        event = {
            'queryStringParameters': {
                'ticketId': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
            }
        }
        context = {}
        
        with patch('src.handlers.exit.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.process_exit.side_effect = Exception("Database connection error")
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'Failed to process parking exit' in body['error']

    def test_ticket_id_normalization(self):
        """Test that ticket ID is normalized (trimmed)."""
        event = {
            'queryStringParameters': {
                'ticketId': '  a1b2c3d4-e5f6-7890-abcd-ef1234567890  '
            }
        }
        context = {}
        
        expected_exit_info = {
            'plate': 'ABC123',
            'totalTimeMinutes': 30,
            'parkingLot': 2,
            'chargeUSD': 5.00
        }
        
        with patch('src.handlers.exit.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.process_exit.return_value = expected_exit_info
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        # Should be called with trimmed ticket ID
        mock_service.process_exit.assert_called_once_with('a1b2c3d4-e5f6-7890-abcd-ef1234567890')

    def test_cors_headers(self):
        """Test that CORS headers are included in response."""
        event = {
            'queryStringParameters': {
                'ticketId': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
            }
        }
        context = {}
        
        expected_exit_info = {
            'plate': 'ABC123',
            'totalTimeMinutes': 15,
            'parkingLot': 1,
            'chargeUSD': 2.50
        }
        
        with patch('src.handlers.exit.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.process_exit.return_value = expected_exit_info
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        headers = response['headers']
        assert headers['Access-Control-Allow-Origin'] == '*'
        assert headers['Content-Type'] == 'application/json'

    def test_uuid_case_insensitive(self):
        """Test that UUID validation is case insensitive."""
        event = {
            'queryStringParameters': {
                'ticketId': 'A1B2C3D4-E5F6-7890-ABCD-EF1234567890'  # Uppercase UUID
            }
        }
        context = {}
        
        expected_exit_info = {
            'plate': 'XYZ789',
            'totalTimeMinutes': 60,
            'parkingLot': 3,
            'chargeUSD': 10.00
        }
        
        with patch('src.handlers.exit.ParkingService') as mock_service_class:
            mock_service = Mock()
            mock_service.process_exit.return_value = expected_exit_info
            mock_service_class.return_value = mock_service
            
            response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body == expected_exit_info 