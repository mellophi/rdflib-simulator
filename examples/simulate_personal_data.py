"""
Example script demonstrating the personal data knowledge graph simulator.
"""

from datetime import datetime
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator

def main():
    # Initialize simulator for a person
    simulator = PersonalDataKnowledgeSimulator(
        person_id="person123",
        start_date=datetime(2024, 1, 1),
        base_uri="http://example.org/personal/"
    )
    
    # Simulate 30 days of data
    print("Simulating 30 days of personal data...")
    simulator.simulate_period(30)
    
    # Export the ontology to a file
    print("Exporting ontology to personal_data.ttl...")
    simulator.export_ontology(format='turtle', file_path='data/personal_data.ttl')
    
    # Example SPARQL queries
    print("\nQuerying the knowledge graph...")
    
    # Query for all flights
    flights_query = """
    PREFIX travel: <http://example.org/personal/travel/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?flight ?number
    WHERE {
        ?flight rdf:type travel:Flight ;
                travel:hasFlightNumber ?number .
    }
    """
    
    flights = simulator.query_data(flights_query)
    print("\nFlights booked:")
    for flight in flights:
        print(f"Flight: {flight['number']}")
    
    # Query for average daily steps
    steps_query = """
    PREFIX health: <http://example.org/personal/health/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    
    SELECT (ROUND(AVG(xsd:integer(?steps))) AS ?average_steps)
    WHERE {
        ?activity rdf:type health:PhysicalActivity ;
                 health:hasSteps ?steps .
    }
    """
    
    steps = simulator.query_data(steps_query)
    if steps and 'average_steps' in steps[0]:
        print(f"\nAverage daily steps: {steps[0]['average_steps']}")
    else:
        print("\nNo step data available")
    
    # Query for hotel bookings
    hotels_query = """
    PREFIX travel: <http://example.org/personal/travel/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    
    SELECT ?hotel ?name ?ref
    WHERE {
        ?hotel rdf:type travel:Hotel ;
               travel:hasName ?name ;
               travel:hasBookingReference ?ref .
    }
    """
    
    hotels = simulator.query_data(hotels_query)
    print("\nHotel bookings:")
    for hotel in hotels:
        print(f"Hotel: {hotel['name']} (Booking ref: {hotel['ref']})")

if __name__ == "__main__":
    main() 