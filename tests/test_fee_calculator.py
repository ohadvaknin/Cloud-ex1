import pytest
from src.services.fee_calculator import FeeCalculator

# AI generated tests

class TestFeeCalculator:
    """Test cases for FeeCalculator class."""

    def test_default_initialization(self):
        """Test default calculator initialization."""
        calculator = FeeCalculator()
        assert calculator.hourly_rate == 10.0
        assert calculator.billing_increment_minutes == 15

    def test_custom_initialization(self):
        """Test calculator with custom rates."""
        calculator = FeeCalculator(hourly_rate=15.0, billing_increment_minutes=30)
        assert calculator.hourly_rate == 15.0
        assert calculator.billing_increment_minutes == 30

    def test_zero_duration_fee(self):
        """Test fee calculation for zero duration."""
        calculator = FeeCalculator()
        assert calculator.calculate_fee(0) == 0.0

    def test_negative_duration_fee(self):
        """Test fee calculation for negative duration."""
        calculator = FeeCalculator()
        assert calculator.calculate_fee(-10) == 0.0

    def test_exact_increment_fee(self):
        """Test fee calculation for exact billing increment."""
        calculator = FeeCalculator()
        # 15 minutes = 0.25 hours * $10 = $2.50
        assert calculator.calculate_fee(15) == 2.50

    def test_partial_increment_fee(self):
        """Test fee calculation rounds up to next increment."""
        calculator = FeeCalculator()
        # 10 minutes rounds up to 15 minutes = $2.50
        assert calculator.calculate_fee(10) == 2.50
        # 16 minutes rounds up to 30 minutes = $5.00
        assert calculator.calculate_fee(16) == 5.00

    def test_multiple_increments_fee(self):
        """Test fee calculation for multiple increments."""
        calculator = FeeCalculator()
        # 60 minutes = 1 hour * $10 = $10.00
        assert calculator.calculate_fee(60) == 10.00
        # 75 minutes rounds up to 90 minutes = 1.5 hours * $10 = $15.00
        # Actually: 75 minutes = 5 increments = 75 minutes = 1.25 hours * $10 = $12.50
        assert calculator.calculate_fee(75) == 12.50

    def test_custom_hourly_rate(self):
        """Test fee calculation with custom hourly rate."""
        calculator = FeeCalculator(hourly_rate=20.0)
        # 60 minutes = 1 hour * $20 = $20.00
        assert calculator.calculate_fee(60) == 20.00

    def test_custom_billing_increment(self):
        """Test fee calculation with custom billing increment."""
        calculator = FeeCalculator(billing_increment_minutes=30)
        # 20 minutes rounds up to 30 minutes = 0.5 hours * $10 = $5.00
        assert calculator.calculate_fee(20) == 5.00

    def test_decimal_precision(self):
        """Test fee calculation decimal precision."""
        calculator = FeeCalculator()
        # 45 minutes = 0.75 hours * $10 = $7.50
        assert calculator.calculate_fee(45) == 7.50

    def test_large_duration(self):
        """Test fee calculation for large duration."""
        calculator = FeeCalculator()
        # 24 hours * 60 minutes = 1440 minutes = $240.00
        assert calculator.calculate_fee(1440) == 240.00

    def test_get_billing_info(self):
        """Test billing information retrieval."""
        calculator = FeeCalculator(hourly_rate=12.5, billing_increment_minutes=20)
        info = calculator.get_billing_info()
        
        expected = {
            'hourly_rate_usd': 12.5,
            'billing_increment_minutes': 20
        }
        assert info == expected

    @pytest.mark.parametrize("duration,expected_fee", [
        (1, 2.50),    # 1 minute -> 15 minutes
        (14, 2.50),   # 14 minutes -> 15 minutes
        (15, 2.50),   # 15 minutes -> 15 minutes
        (16, 5.00),   # 16 minutes -> 30 minutes
        (30, 5.00),   # 30 minutes -> 30 minutes
        (31, 7.50),   # 31 minutes -> 45 minutes
        (45, 7.50),   # 45 minutes -> 45 minutes
        (46, 10.00),  # 46 minutes -> 60 minutes
        (60, 10.00),  # 60 minutes -> 60 minutes
        (90, 15.00),  # 90 minutes -> 90 minutes
        (120, 20.00), # 120 minutes -> 120 minutes
    ])
    def test_fee_calculation_scenarios(self, duration, expected_fee):
        """Test various fee calculation scenarios."""
        calculator = FeeCalculator()
        assert calculator.calculate_fee(duration) == expected_fee 