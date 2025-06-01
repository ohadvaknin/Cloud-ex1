from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
import uuid


@dataclass
class ParkingTicket:
    """Data model for parking tickets."""
    
    ticket_id: str
    plate: str
    parking_lot: int
    entry_time: datetime
    exit_time: Optional[datetime] = None
    
    @classmethod
    def create_new(cls, plate: str, parking_lot: int) -> 'ParkingTicket':
        """Create a new parking ticket with generated ID and current timestamp."""
        return cls(
            ticket_id=str(uuid.uuid4()),
            plate=plate.strip(),
            parking_lot=parking_lot,
            entry_time=datetime.utcnow()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ticket to dictionary for DynamoDB storage."""
        return {
            'ticket_id': self.ticket_id,
            'plate': self.plate,
            'parking_lot': self.parking_lot,
            'entry_time': self.entry_time.isoformat(),
            'exit_time': self.exit_time.isoformat() if self.exit_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParkingTicket':
        """Create ticket from DynamoDB data."""
        return cls(
            ticket_id=data['ticket_id'],
            plate=data['plate'],
            parking_lot=int(data['parking_lot']),
            entry_time=datetime.fromisoformat(data['entry_time']),
            exit_time=datetime.fromisoformat(data['exit_time']) if data.get('exit_time') else None
        )
    
    def mark_exit(self) -> None:
        """Mark ticket as exited with current timestamp."""
        self.exit_time = datetime.utcnow()
    
    def get_duration_minutes(self) -> int:
        """Calculate parking duration in minutes."""
        if not self.exit_time:
            raise ValueError("Cannot calculate duration without exit time")
        
        duration = self.exit_time - self.entry_time
        return int(duration.total_seconds() / 60) 