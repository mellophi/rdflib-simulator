"""
Specialized ontology builder for personal health and travel data.
"""

from rdflib import Namespace, URIRef, Literal, XSD, RDF
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
        self.general = Namespace(base_uri + "general/")
        self.person = Namespace(base_uri + "person/")

        # Bind namespaces
        self.gm.graph.bind('health', self.health)
        self.gm.graph.bind('travel', self.travel)
        self.gm.graph.bind('location', self.location)
        self.gm.graph.bind('time', self.time)
        self.gm.graph.bind('general', self.general)
        self.gm.graph.bind('person', self.person)
        # Initialize ontology structure
        self._initialize_ontology()
        
    def _initialize_ontology(self):
        """Initialize the basic ontology structure with classes and properties."""
        # Person class
        self.create_class(self.person.Person, label="Person")

        # General-related classes
        self.create_class(self.general.Others, label="Other activities")

        # Health-related classes
        self.create_class(self.health.HealthMetric, label="Health Metric")
        self.create_class(self.health.PhysicalActivity, label="Physical Activity")
        self.create_class(self.health.VitalSigns, label="Vital Signs")
        self.create_class(self.health.Sleep, label="Sleep")
        
        # Travel-related classes
        self.create_class(self.travel.Booking, label="Travel Booking")
        self.create_class(self.travel.Flight, label="Flight")
        self.create_class(self.travel.Hotel, label="Hotel")
        self.create_class(self.location.Airport, label="Airport")
        self.create_class(self.location.City, label="City")
        self.create_class(self.travel.Place, label="Travel Place")

        # Properties for person
        self.create_property(self.person.hasHealthData, "ObjectProperty",
                           domain=self.person.Person,
                           range_=self.health.HealthMetric)
        self.create_property(self.person.hasTravelBooking, "ObjectProperty",
                           domain=self.person.Person,
                           range_=self.travel.Booking)
        self.create_property(self.person.hasActivity, "ObjectProperty",
                           domain=self.person.Person,
                           range_=self.general.Others)
        self.create_property(self.person.travelTo, "ObjectProperty",
                           domain=self.person.Person,
                           range_=self.travel.Place)

        #Properties for general
        self.create_property(self.general.hasActivity, "ObjectProperty",
                           domain=self.general.Others,
                           range_=self.general.OtherActivity)
        
        # Properties for health metrics
        self.create_property(self.health.hasSteps, "DatatypeProperty",
                           domain=self.health.PhysicalActivity,
                           range_=XSD.integer)
        self.create_property(self.health.hasHeartRate, "DatatypeProperty",
                           domain=self.health.VitalSigns,
                           range_=XSD.integer)
        self.create_property(self.health.hasCaloriesBurned, "DatatypeProperty",
                           domain=self.health.PhysicalActivity,
                           range_=XSD.integer)
        self.create_property(self.health.timestamp, "DatatypeProperty",
                           domain=self.health.HealthMetric,
                           range_=XSD.dateTime)
        
        # Properties for travel
        self.create_property(self.travel.hasBookingReference, "DatatypeProperty",
                           domain=self.travel.Booking,
                           range_=XSD.string)
        self.create_property(self.travel.hasDeparture, "ObjectProperty",
                           domain=self.travel.Flight,
                           range_=self.location.Airport)
        self.create_property(self.travel.hasArrival, "ObjectProperty",
                           domain=self.travel.Flight,
                           range_=self.location.Airport)
        self.create_property(self.travel.hasName, "DatatypeProperty",
                           domain=self.travel.Hotel,
                           range_=XSD.string)
        self.create_property(self.travel.placeName, "DatatypeProperty",
                           domain=self.travel.Place,
                           range_=XSD.string)
        self.create_property(self.travel.placeTime, "DatatypeProperty",
                           domain=self.travel.Place,
                           range_=XSD.dateTime)
        self.create_property(self.travel.placeInfo, "DatatypeProperty",
                            domain=self.travel.Place,
                           range_=XSD.string)
        
    def add_general_activity(self, person_id: str, date: str):
        """
        Add general activity data to the ontology.
        
        Args:
            activity: Currently "general:None" is the only option
        """
        # Create person instance if not exists
        person_uri = self.person[f"person_{person_id}"]
        self.gm.add_triple(person_uri, RDF.type, self.person.Person)

        timestamp = int(datetime.fromisoformat(date).timestamp())
        activity_id = self.general[f"activity_{timestamp}"]
        self.gm.add_triple(activity_id, RDF.type, self.general.Others)
        self.gm.add_triple(activity_id, self.general.hasActivity, self.general.OtherActivity)
        
        # Link activity to person
        self.gm.add_triple(person_uri, self.person.hasActivity, activity_id)

    def add_health_data(self, data: Dict[str, Any], person_id: str):
        """
        Add daily health data to the ontology.
        
        Args:
            data: Dictionary containing health metrics
            person_id: Identifier for the person
        """
        # Create person instance if not exists
        person_uri = self.person[f"person_{person_id}"]
        self.gm.add_triple(person_uri, RDF.type, self.person.Person)

        date = data['date'] 
        timestamp = int(datetime.fromisoformat(date).timestamp())
        metrics_id = self.health[f"metrics_{timestamp}"]
        
        # Add physical activity
        activity_id = self.health[f"activity_{timestamp}"]
        self.gm.add_triple(activity_id, RDF.type, self.health.PhysicalActivity)
        self.gm.add_triple(activity_id, self.health.hasSteps, data['steps'])
        self.gm.add_triple(activity_id, self.health.hasCaloriesBurned, data['calories_burned'])
        self.gm.add_triple(activity_id, self.health.timestamp, date, XSD.dateTime.toPython())
        
        # Add vital signs
        vitals_id = self.health[f"vitals_{timestamp}"]
        self.gm.add_triple(vitals_id, RDF.type, self.health.VitalSigns)
        self.gm.add_triple(vitals_id, self.health.hasHeartRate, data['heart_rate']['average'])
        self.gm.add_triple(vitals_id, self.health.hasBloodPressureSystolic,
                          data['blood_pressure']['systolic'])
        self.gm.add_triple(vitals_id, self.health.hasBloodPressureDiastolic,
                          data['blood_pressure']['diastolic'])
        self.gm.add_triple(vitals_id, self.health.timestamp, date, XSD.dateTime.toPython())
        
        # Add sleep data
        sleep_id = self.health[f"sleep_{timestamp}"]
        self.gm.add_triple(sleep_id, RDF.type, self.health.Sleep)
        self.gm.add_triple(sleep_id, self.health.hasDuration, data['sleep']['duration'])
        self.gm.add_triple(sleep_id, self.health.hasDeepSleep, data['sleep']['deep_sleep'])
        self.gm.add_triple(sleep_id, self.health.hasREMSleep, data['sleep']['rem_sleep'])
        self.gm.add_triple(sleep_id, self.health.timestamp, date, XSD.dateTime.toPython())

        # Link all health data to person
        self.gm.add_triple(person_uri, self.person.hasHealthData, activity_id)
        self.gm.add_triple(person_uri, self.person.hasHealthData, vitals_id)
        self.gm.add_triple(person_uri, self.person.hasHealthData, sleep_id)

    def add_travel_booking(self, booking_data: Dict[str, Any], person_id: str) -> None:
        """Add travel booking data to the ontology."""
        # Create booking instance
        # print(booking_data)
        person_uri = self.person[f"person_{person_id}"]
        self.gm.add_triple(person_uri, RDF.type, self.person.Person)
        
        booking_id = booking_data['booking_id']
        booking_uri = self.travel[f"booking_{booking_id}"]
        self.gm.add_triple(booking_uri, RDF.type, self.travel.Booking)
        self.gm.add_triple(booking_uri, self.travel.bookingId, Literal(booking_id))
        self.gm.add_triple(booking_uri, self.travel.bookingDate, Literal(booking_data['booking_date'], datatype=XSD.dateTime))
        
        # Link booking to person
        self.gm.add_triple(person_uri, self.person.hasTravelBooking, booking_uri)
        
        # Add outbound flight details
        outbound_flight_uri = self.travel[f"flight_{booking_data['flight']['flight_number']}"]
        self.gm.add_triple(outbound_flight_uri, RDF.type, self.travel.Flight)
        self.gm.add_triple(outbound_flight_uri, self.travel.flightNumber, Literal(booking_data['flight']['flight_number']))
        self.gm.add_triple(outbound_flight_uri, self.travel.airline, Literal(booking_data['flight']['airline']))
        
        # Add departure details
        departure = booking_data['flight']['departure']
        self.gm.add_triple(outbound_flight_uri, self.travel.departureAirport, Literal(departure['airport']))
        self.gm.add_triple(outbound_flight_uri, self.travel.departureCity, Literal(departure['city']))
        self.gm.add_triple(outbound_flight_uri, self.travel.departureCountry, Literal(departure['country']))
        self.gm.add_triple(outbound_flight_uri, self.travel.departureDateTime, Literal(departure['datetime'], datatype=XSD.dateTime))
        
        # Add arrival details
        arrival = booking_data['flight']['arrival']
        self.gm.add_triple(outbound_flight_uri, self.travel.arrivalAirport, Literal(arrival['airport']))
        self.gm.add_triple(outbound_flight_uri, self.travel.arrivalCity, Literal(arrival['city']))
        self.gm.add_triple(outbound_flight_uri, self.travel.arrivalCountry, Literal(arrival['country']))
        self.gm.add_triple(outbound_flight_uri, self.travel.arrivalDateTime, Literal(arrival['datetime'], datatype=XSD.dateTime))
        
        # Link outbound flight to booking
        self.gm.add_triple(booking_uri, self.travel.hasOutboundFlight, outbound_flight_uri)
        
        # Add return flight details if present
        if 'return_flight' in booking_data:
            return_flight_uri = self.travel[f"flight_{booking_data['return_flight']['flight_number']}"]
            self.gm.add_triple(return_flight_uri, RDF.type, self.travel.Flight)
            self.gm.add_triple(return_flight_uri, self.travel.flightNumber, Literal(booking_data['return_flight']['flight_number']))
            self.gm.add_triple(return_flight_uri, self.travel.airline, Literal(booking_data['return_flight']['airline']))
            
            # Add return departure details
            return_departure = booking_data['return_flight']['departure']
            self.gm.add_triple(return_flight_uri, self.travel.departureAirport, Literal(return_departure['airport']))
            self.gm.add_triple(return_flight_uri, self.travel.departureCity, Literal(return_departure['city']))
            self.gm.add_triple(return_flight_uri, self.travel.departureCountry, Literal(return_departure['country']))
            self.gm.add_triple(return_flight_uri, self.travel.departureDateTime, Literal(return_departure['datetime'], datatype=XSD.dateTime))
            
            # Add return arrival details
            return_arrival = booking_data['return_flight']['arrival']
            self.gm.add_triple(return_flight_uri, self.travel.arrivalAirport, Literal(return_arrival['airport']))
            self.gm.add_triple(return_flight_uri, self.travel.arrivalCity, Literal(return_arrival['city']))
            self.gm.add_triple(return_flight_uri, self.travel.arrivalCountry, Literal(return_arrival['country']))
            self.gm.add_triple(return_flight_uri, self.travel.arrivalDateTime, Literal(return_arrival['datetime'], datatype=XSD.dateTime))
            
            # Link return flight to booking
            self.gm.add_triple(booking_uri, self.travel.hasReturnFlight, return_flight_uri)
        
        # Add hotel details
        hotel = booking_data['hotel']
        hotel_uri = self.travel[f"hotel_booking_{booking_id}"]
        self.gm.add_triple(hotel_uri, RDF.type, self.travel.HotelBooking)
        self.gm.add_triple(hotel_uri, self.travel.hotelName, Literal(hotel['name']))
        self.gm.add_triple(hotel_uri, self.travel.checkInDate, Literal(hotel['check_in'], datatype=XSD.dateTime))
        self.gm.add_triple(hotel_uri, self.travel.checkOutDate, Literal(hotel['check_out'], datatype=XSD.dateTime))
        self.gm.add_triple(hotel_uri, self.travel.city, Literal(hotel['city']))
        self.gm.add_triple(hotel_uri, self.travel.country, Literal(hotel['country']))
        self.gm.add_triple(hotel_uri, self.travel.roomType, Literal(hotel['room_type']))
        self.gm.add_triple(hotel_uri, self.travel.bookingReference, Literal(hotel['booking_reference']))
        
        # Link hotel booking to travel booking
        self.gm.add_triple(booking_uri, self.travel.hasHotelBooking, hotel_uri)

        # Add Place information
        place_id = self.travel[f"place_{booking_id}"]
        self.gm.add_triple(place_id, RDF.type, self.travel.Place)
        self.gm.add_triple(place_id, self.travel.placeName, 
                          Literal(booking_data['flight']['arrival']['city'], datatype=XSD.string))
        self.gm.add_triple(place_id, self.travel.placeTime,
                          booking_data['flight']['arrival']['datetime'], XSD.dateTime.toPython())
        
        # Link Place to Person
        self.gm.add_triple(person_uri, self.person.travelTo, place_id)