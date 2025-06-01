import math
from typing import Optional
import os


class FeeCalculator:
    """Modular fee calculation service for parking charges."""
    
    def __init__(self, hourly_rate: Optional[float] = None, billing_increment_minutes: Optional[int] = None):
        """
        Initialize fee calculator with configurable rates.
        
        Args:
            hourly_rate: Rate per hour in USD (default: $10/hour)
            billing_increment_minutes: Billing increment in minutes (default: 15 minutes)
        """
        self.hourly_rate = hourly_rate or float(os.getenv('HOURLY_RATE', '10.0'))
        self.billing_increment_minutes = billing_increment_minutes or int(os.getenv('BILLING_INCREMENT_MINUTES', '15'))
    
    def calculate_fee(self, duration_minutes: int) -> float:
        """
        Calculate parking fee based on duration.
        
        Args:
            duration_minutes: Total parking duration in minutes
            
        Returns:
            Fee in USD rounded to 2 decimal places
        """
        if duration_minutes <= 0:
            return 0.0
        
        # Round up to next billing increment
        billable_minutes = math.ceil(duration_minutes / self.billing_increment_minutes) * self.billing_increment_minutes
        
        # Calculate fee based on hourly rate
        fee = (billable_minutes / 60) * self.hourly_rate
        
        # Round to 2 decimal places
        return round(fee, 2)
    
    def get_billing_info(self) -> dict:
        """Get current billing configuration."""
        return {
            'hourly_rate_usd': self.hourly_rate,
            'billing_increment_minutes': self.billing_increment_minutes
        }


# Default instance for easy import
default_calculator = FeeCalculator() 