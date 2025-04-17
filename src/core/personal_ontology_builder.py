"""
Specialized ontology builder for personal health and travel data.
"""

from rdflib import Namespace, URIRef, Literal, XSD
from typing import Dict, Any
from .ontology_builder import OntologyBuilder
from datetime import datetime
import urllib.parse

class PersonalOntologyBuilder(OntologyBuilder):
    def __init__(self, base_uri: str = "http://example.org/personal/"):
        """
        Initialize PersonalOntologyBuilder with specific namespaces for personal data.
        """
        super().__init__()
        
        # Define specific namespaces
        self.health = Namespace(base_uri + "health/")
        self.travel = Namespace(base_uri + "travel/")
        self.location = Namespace(base_uri + "location/")
        self.time = Namespace(base_uri + "time/")
        
        # Bind namespaces
        self.gm.graph.bind('health', self.health)
        self.gm.graph.bind('travel', self.travel)
        self.gm.graph.bind('location', self.location)
        self.gm.graph.bind('time', self.time)
        
        # Initialize ontology structure
        self._initialize_ontology()
        
    def _initialize_ontology(self):
        """Initialize the basic ontology structure with classes and properties."""
        # Health-related classes
        self.create_class("health:HealthMetric", label="Health Metric")
        self.create_class("health:PhysicalActivity", label="Physical Activity")
        self.create_class("health:VitalSigns", label="Vital Signs")
        self.create_class("health:Sleep", label="Sleep")
        
        # Travel-related classes
        self.create_class("travel:Booking", label="Travel Booking")
        self.create_class("travel:Flight", label="Flight")
        self.create_class("travel:Hotel", label="Hotel")
        self.create_class("location:Airport", label="Airport")
        self.create_class("location:City", label="City")
        
        # Properties for health metrics
        self.create_property("health:hasSteps", "DatatypeProperty",
                           domain="health:PhysicalActivity",
                           range_=XSD.integer)
        self.create_property("health:hasHeartRate", "DatatypeProperty",
                           domain="health:VitalSigns",
                           range_=XSD.integer)
        self.create_property("health:hasCaloriesBurned", "DatatypeProperty",
                           domain="health:PhysicalActivity",
                           range_=XSD.integer)
        
        # Properties for travel
        self.create_property("travel:hasBookingReference", "DatatypeProperty",
                           domain="travel:Booking",
                           range_=XSD.string)
        self.create_property("travel:hasDeparture", "ObjectProperty",
                           domain="travel:Flight",
                           range_="location:Airport")
        self.create_property("travel:hasArrival", "ObjectProperty",
                           domain="travel:Flight",
                           range_="location:Airport")
        self.create_property("travel:hasName", "DatatypeProperty",
                           domain="travel:Hotel",
                           range_=XSD.string)

    def add_health_data(self, data: Dict[str, Any], person_id: str):
        """
        Add daily health data to the ontology.
        
        Args:
            data: Dictionary containing health metrics
            person_id: Identifier for the person
        """
        date = data['date']
        metrics_id = f"health:metrics_{person_id}_{date}"
        
        # Add physical activity
        activity_id = f"health:activity_{person_id}_{date}"
        self.gm.add_triple(activity_id, "rdf:type", "health:PhysicalActivity")
        self.gm.add_triple(activity_id, "health:hasSteps", data['steps'])
        self.gm.add_triple(activity_id, "health:hasCaloriesBurned", data['calories_burned'])
        
        # Add vital signs
        vitals_id = f"health:vitals_{person_id}_{date}"
        self.gm.add_triple(vitals_id, "rdf:type", "health:VitalSigns")
        self.gm.add_triple(vitals_id, "health:hasHeartRate", data['heart_rate']['average'])
        self.gm.add_triple(vitals_id, "health:hasBloodPressureSystolic",
                          data['blood_pressure']['systolic'])
        self.gm.add_triple(vitals_id, "health:hasBloodPressureDiastolic",
                          data['blood_pressure']['diastolic'])
        
        # Add sleep data
        sleep_id = f"health:sleep_{person_id}_{date}"
        self.gm.add_triple(sleep_id, "rdf:type", "health:Sleep")
        self.gm.add_triple(sleep_id, "health:hasDuration", data['sleep']['duration'])
        self.gm.add_triple(sleep_id, "health:hasDeepSleep", data['sleep']['deep_sleep'])
        self.gm.add_triple(sleep_id, "health:hasREMSleep", data['sleep']['rem_sleep'])

    def add_travel_booking(self, booking: Dict[str, Any], person_id: str):
        """
        Add travel booking data to the ontology.
        
        Args:
            booking: Dictionary containing booking details
            person_id: Identifier for the person
        """
        booking_id = f"travel:booking_{booking['booking_id']}"
        self.gm.add_triple(booking_id, "rdf:type", "travel:Booking")
        self.gm.add_triple(booking_id, "travel:hasBookingReference", 
                          Literal(booking['booking_id'], datatype=XSD.string))
        
        # Add outbound flight
        flight = booking['flight']
        flight_id = f"travel:flight_{booking['booking_id']}_outbound"
        self.gm.add_triple(flight_id, "rdf:type", "travel:Flight")
        self.gm.add_triple(flight_id, "travel:hasFlightNumber", 
                          Literal(flight['flight_number'], datatype=XSD.string))
        
        # Add departure and arrival airports
        dep_airport_id = f"location:airport_{flight['departure']['airport']}"
        arr_airport_id = f"location:airport_{flight['arrival']['airport']}"
        
        self.gm.add_triple(dep_airport_id, "rdf:type", "location:Airport")
        self.gm.add_triple(arr_airport_id, "rdf:type", "location:Airport")
        
        self.gm.add_triple(flight_id, "travel:hasDeparture", dep_airport_id)
        self.gm.add_triple(flight_id, "travel:hasArrival", arr_airport_id)
        
        # Add hotel booking
        hotel = booking['hotel']
        hotel_id = f"travel:hotel_{booking['booking_id']}"
        self.gm.add_triple(hotel_id, "rdf:type", "travel:Hotel")
        self.gm.add_triple(hotel_id, "travel:hasName", 
                          Literal(hotel['name'], datatype=XSD.string))
        self.gm.add_triple(hotel_id, "travel:hasBookingReference", 
                          Literal(hotel['booking_reference'], datatype=XSD.string))
        
        # Link everything to the booking
        self.gm.add_triple(booking_id, "travel:hasFlight", flight_id)
        self.gm.add_triple(booking_id, "travel:hasHotel", hotel_id)
        self.gm.add_triple(booking_id, "travel:hasBookingDate", 
                          Literal(booking['booking_date'], datatype=XSD.date)) 