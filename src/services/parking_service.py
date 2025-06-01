import boto3
import os
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError

from src.models.parking_ticket import ParkingTicket
from src.services.fee_calculator import default_calculator


class ParkingService:
    """Service for managing parking tickets and DynamoDB operations."""
    
    def __init__(self):
        """Initialize service with DynamoDB client."""
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.getenv('PARKING_TABLE_NAME', 'parking-tickets')
        self.table = self.dynamodb.Table(self.table_name)
        self.fee_calculator = default_calculator
    
    def create_entry(self, plate: str, parking_lot: int) -> str:
        """
        Create a new parking entry.
        
        Args:
            plate: License plate number
            parking_lot: Parking lot identifier
            
        Returns:
            Generated ticket ID
            
        Raises:
            Exception: If DynamoDB operation fails
        """
        ticket = ParkingTicket.create_new(plate, parking_lot)
        
        try:
            self.table.put_item(Item=ticket.to_dict())
            return ticket.ticket_id
        except ClientError as e:
            raise Exception(f"Failed to create parking entry: {e.response['Error']['Message']}")
    
    def process_exit(self, ticket_id: str) -> Dict[str, Any]:
        """
        Process parking exit and calculate charges.
        
        Args:
            ticket_id: Unique ticket identifier
            
        Returns:
            Dictionary with exit information and charges
            
        Raises:
            ValueError: If ticket not found or already processed
            Exception: If DynamoDB operation fails
        """
        try:
            # Get ticket from database
            response = self.table.get_item(Key={'ticket_id': ticket_id})
            
            if 'Item' not in response:
                raise ValueError(f"Ticket {ticket_id} not found")
            
            ticket = ParkingTicket.from_dict(response['Item'])
            
            # Check if already exited
            if ticket.exit_time:
                raise ValueError(f"Ticket {ticket_id} already processed")
            
            # Mark exit and calculate charges
            ticket.mark_exit()
            duration_minutes = ticket.get_duration_minutes()
            charge_usd = self.fee_calculator.calculate_fee(duration_minutes)
            
            # Update ticket in database
            self.table.update_item(
                Key={'ticket_id': ticket_id},
                UpdateExpression='SET exit_time = :exit_time',
                ExpressionAttributeValues={':exit_time': ticket.exit_time.isoformat()}
            )
            
            return {
                'plate': ticket.plate,
                'totalTimeMinutes': duration_minutes,
                'parkingLot': ticket.parking_lot,
                'chargeUSD': charge_usd
            }
            
        except ClientError as e:
            raise Exception(f"Failed to process exit: {e.response['Error']['Message']}")
    
    def get_ticket(self, ticket_id: str) -> Optional[ParkingTicket]:
        """
        Retrieve a parking ticket by ID.
        
        Args:
            ticket_id: Unique ticket identifier
            
        Returns:
            ParkingTicket object or None if not found
        """
        try:
            response = self.table.get_item(Key={'ticket_id': ticket_id})
            
            if 'Item' in response:
                return ParkingTicket.from_dict(response['Item'])
            return None
            
        except ClientError:
            return None 