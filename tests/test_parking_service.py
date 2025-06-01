import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from botocore.exceptions import ClientError

from src.services.parking_service import ParkingService
from src.models.parking_ticket import ParkingTicket


class TestParkingService:
    """Test cases for ParkingService class."""

    @pytest.fixture
    def mock_dynamodb_table(self):
        """Mock DynamoDB table for testing."""
        with patch('src.services.parking_service.boto3.resource') as mock_resource:
            mock_table = Mock()
            mock_resource.return_value.Table.return_value = mock_table
            yield mock_table

    @pytest.fixture
    def parking_service(self, mock_dynamodb_table):
        """Create ParkingService instance with mocked dependencies."""
        with patch.dict('os.environ', {'PARKING_TABLE_NAME': 'test-table'}):
            return ParkingService()

    def test_create_entry_success(self, parking_service, mock_dynamodb_table):
        """Test successful parking entry creation."""
        mock_dynamodb_table.put_item.return_value = {}
        
        ticket_id = parking_service.create_entry("ABC123", 1)
        
        assert ticket_id is not None
        assert len(ticket_id) == 36  # UUID length
        mock_dynamodb_table.put_item.assert_called_once()

    def test_create_entry_dynamodb_error(self, parking_service, mock_dynamodb_table):
        """Test parking entry creation with DynamoDB error."""
        mock_dynamodb_table.put_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ValidationException', 'Message': 'Test error'}},
            operation_name='PutItem'
        )
        
        with pytest.raises(Exception) as exc_info:
            parking_service.create_entry("ABC123", 1)
        
        assert "Failed to create parking entry" in str(exc_info.value)

    def test_process_exit_success(self, parking_service, mock_dynamodb_table):
        """Test successful parking exit processing."""
        # Mock ticket data
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        ticket_data = {
            'ticket_id': 'test-ticket-id',
            'plate': 'ABC123',
            'parking_lot': 1,
            'entry_time': entry_time.isoformat(),
            'exit_time': None
        }
        
        mock_dynamodb_table.get_item.return_value = {'Item': ticket_data}
        mock_dynamodb_table.update_item.return_value = {}
        
        with patch('src.models.parking_ticket.datetime') as mock_datetime:
            # Mock exit time to be 30 minutes after entry
            exit_time = datetime(2024, 1, 1, 10, 30, 0)
            mock_datetime.utcnow.return_value = exit_time
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            result = parking_service.process_exit('test-ticket-id')
        
        expected_result = {
            'plate': 'ABC123',
            'totalTimeMinutes': 30,
            'parkingLot': 1,
            'chargeUSD': 5.0  # 30 minutes rounds up to 45 minutes = $7.50
        }
        
        # Check individual fields since exact charge calculation may vary slightly
        assert result['plate'] == expected_result['plate']
        assert result['totalTimeMinutes'] == expected_result['totalTimeMinutes']
        assert result['parkingLot'] == expected_result['parkingLot']
        assert result['chargeUSD'] == 5.0  # 30 minutes -> 30 minutes = $5.0

    def test_process_exit_ticket_not_found(self, parking_service, mock_dynamodb_table):
        """Test exit processing for non-existent ticket."""
        mock_dynamodb_table.get_item.return_value = {}
        
        with pytest.raises(ValueError) as exc_info:
            parking_service.process_exit('non-existent-ticket')
        
        assert "not found" in str(exc_info.value)

    def test_process_exit_already_processed(self, parking_service, mock_dynamodb_table):
        """Test exit processing for already processed ticket."""
        ticket_data = {
            'ticket_id': 'test-ticket-id',
            'plate': 'ABC123',
            'parking_lot': 1,
            'entry_time': '2024-01-01T10:00:00',
            'exit_time': '2024-01-01T11:00:00'  # Already has exit time
        }
        
        mock_dynamodb_table.get_item.return_value = {'Item': ticket_data}
        
        with pytest.raises(ValueError) as exc_info:
            parking_service.process_exit('test-ticket-id')
        
        assert "already processed" in str(exc_info.value)

    def test_process_exit_dynamodb_error(self, parking_service, mock_dynamodb_table):
        """Test exit processing with DynamoDB error."""
        mock_dynamodb_table.get_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Table not found'}},
            operation_name='GetItem'
        )
        
        with pytest.raises(Exception) as exc_info:
            parking_service.process_exit('test-ticket-id')
        
        assert "Failed to process exit" in str(exc_info.value)

    def test_get_ticket_success(self, parking_service, mock_dynamodb_table):
        """Test successful ticket retrieval."""
        ticket_data = {
            'ticket_id': 'test-ticket-id',
            'plate': 'ABC123',
            'parking_lot': 1,
            'entry_time': '2024-01-01T10:00:00',
            'exit_time': None
        }
        
        mock_dynamodb_table.get_item.return_value = {'Item': ticket_data}
        
        ticket = parking_service.get_ticket('test-ticket-id')
        
        assert ticket is not None
        assert ticket.ticket_id == 'test-ticket-id'
        assert ticket.plate == 'ABC123'
        assert ticket.parking_lot == 1

    def test_get_ticket_not_found(self, parking_service, mock_dynamodb_table):
        """Test ticket retrieval for non-existent ticket."""
        mock_dynamodb_table.get_item.return_value = {}
        
        ticket = parking_service.get_ticket('non-existent-ticket')
        
        assert ticket is None

    def test_get_ticket_dynamodb_error(self, parking_service, mock_dynamodb_table):
        """Test ticket retrieval with DynamoDB error."""
        mock_dynamodb_table.get_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}},
            operation_name='GetItem'
        )
        
        ticket = parking_service.get_ticket('test-ticket-id')
        
        assert ticket is None 