"""
Data simulator for generating synthetic health and travel data.
"""

import random
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Any, Optional

class PersonalDataSimulator:
    def __init__(self, start_date: Optional[datetime] = None):
        """
        Initialize the data simulator.
        
        Args:
            start_date: Starting date for the simulation (defaults to current date)
        """
        self.start_date = start_date or datetime.now()
        self.current_date = self.start_date
        
        # Health metrics ranges (realistic values)
        self.health_ranges = {
            'steps': (2000, 15000),
            'heart_rate': (60, 100),
            'sleep_hours': (5, 9),
            'calories_burned': (1800, 3500),
            'blood_pressure_systolic': (110, 130),
            'blood_pressure_diastolic': (70, 85),
            'weight_kg': (50, 100)
        }
        
        # Common travel destinations
        self.airports = [
            ('JFK', 'New York', 'USA'),
            ('LHR', 'London', 'UK'),
            ('CDG', 'Paris', 'France'),
            ('DXB', 'Dubai', 'UAE'),
            ('SIN', 'Singapore', 'Singapore')
        ]
        
        # Hotel chains
        self.hotels = [
            'Marriott', 'Hilton', 'Hyatt', 'Sheraton',
            'Four Seasons', 'Ritz-Carlton', 'W Hotels'
        ]

    def generate_daily_health_data(self) -> Dict[str, Any]:
        """Generate synthetic health data for a single day."""
        return {
            'date': self.current_date.isoformat(),
            'steps': random.randint(*self.health_ranges['steps']),
            'heart_rate': {
                'average': random.randint(*self.health_ranges['heart_rate']),
                'max': random.randint(100, 140),
                'min': random.randint(45, 60)
            },
            'sleep': {
                'duration': round(random.uniform(*self.health_ranges['sleep_hours']), 2),
                'deep_sleep': round(random.uniform(1, 3), 2),
                'rem_sleep': round(random.uniform(1, 2.5), 2)
            },
            'calories_burned': random.randint(*self.health_ranges['calories_burned']),
            'blood_pressure': {
                'systolic': random.randint(*self.health_ranges['blood_pressure_systolic']),
                'diastolic': random.randint(*self.health_ranges['blood_pressure_diastolic'])
            },
            'weight': round(random.uniform(*self.health_ranges['weight_kg']), 1)
        }

    def generate_travel_booking(self) -> Dict[str, Any]:
        """Generate synthetic travel booking data."""
        # Select random airports for departure and arrival
        departure, arrival = random.sample(self.airports, 2)
        
        # Generate random dates for the trip
        departure_date = self.current_date + timedelta(days=random.randint(7, 30))
        return_date = departure_date + timedelta(days=random.randint(2, 14))
        
        # Generate random times
        departure_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00"
        arrival_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00"
        
        # Combine date and time into datetime objects
        departure_datetime = datetime.fromisoformat(f"{departure_date.date()}T{departure_time}")
        arrival_datetime = datetime.fromisoformat(f"{departure_date.date()}T{arrival_time}")
        
        # Generate booking details
        booking = {
            'booking_id': str(uuid.uuid4()),
            'booking_date': self.current_date.isoformat(),
            'flight': {
                'departure': {
                    'airport': departure[0],
                    'city': departure[1],
                    'country': departure[2],
                    'datetime': departure_datetime.isoformat()
                },
                'arrival': {
                    'airport': arrival[0],
                    'city': arrival[1],
                    'country': arrival[2],
                    'datetime': arrival_datetime.isoformat()
                },
                'airline': random.choice(['Emirates', 'British Airways', 'Lufthansa', 'Singapore Airlines']),
                'flight_number': f"{random.choice(['EK', 'BA', 'LH', 'SQ'])}{random.randint(100, 999)}"
            },
            'hotel': {
                'name': random.choice(self.hotels),
                'check_in': departure_date.isoformat(),
                'check_out': return_date.isoformat(),
                'city': arrival[1],
                'country': arrival[2],
                'room_type': random.choice(['Standard', 'Deluxe', 'Suite']),
                'booking_reference': f"HB{random.randint(10000, 99999)}"
            }
        }
        
        # Add return flight
        return_departure_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00"
        return_arrival_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00"
        
        # Combine return date and time into datetime objects
        return_departure_datetime = datetime.fromisoformat(f"{return_date.date()}T{return_departure_time}")
        return_arrival_datetime = datetime.fromisoformat(f"{return_date.date()}T{return_arrival_time}")
        
        booking['return_flight'] = {
            'departure': {
                'airport': arrival[0],
                'city': arrival[1],
                'country': arrival[2],
                'datetime': return_departure_datetime.isoformat()
            },
            'arrival': {
                'airport': departure[0],
                'city': departure[1],
                'country': departure[2],
                'datetime': return_arrival_datetime.isoformat()
            },
            'airline': random.choice(['Emirates', 'British Airways', 'Lufthansa', 'Singapore Airlines']),
            'flight_number': f"{random.choice(['EK', 'BA', 'LH', 'SQ'])}{random.randint(100, 999)}"
        }
        
        return booking

    def advance_day(self) -> None:
        """Advance the simulation by one day."""
        self.current_date += timedelta(days=1) 