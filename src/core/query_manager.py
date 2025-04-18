"""
Query manager for retrieving temporal data from the knowledge graph.
"""

from datetime import datetime
from typing import Dict, List, Optional
from rdflib import Graph, Namespace, URIRef, Literal, XSD
from rdflib.namespace import RDF, RDFS

class QueryManager:
    def __init__(self, graph):
        """Initialize the query manager with an RDF graph."""
        self.graph = graph
        self.base_uri = "http://example.org/personal/"
        self.prefixes = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX person: <http://example.org/personal/person/>
            PREFIX health: <http://example.org/personal/health/>
            PREFIX travel: <http://example.org/personal/travel/>
            PREFIX location: <http://example.org/personal/location/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        """

    def get_health_data(self, start_date: datetime, end_date: datetime, person_uri: str) -> List[Dict[str, any]]:
        """Query health data for a person within a date range."""
        # First, let's just get all health data for the person
        query = self.prefixes + """
            SELECT DISTINCT ?activity_type ?date 
            WHERE {
                ?person rdf:type person:Person .
                ?person person:hasHealthData ?activity .
                ?activity health:timestamp ?date .
                ?activity a ?activity_type .
                FILTER(?date >= """ + f'"{start_date.isoformat()}"^^xsd:dateTime' + """ && 
                       ?date <= """ + f'"{end_date.isoformat()}"^^xsd:dateTime' + """)
            }
            ORDER BY ?date
        """
        
        # print("\nDebug - Health data query:")
        # print(query)
        
        results = []
        for row in self.graph.query(query):
            print(f"Found health data: {row.activity_type} {row.date}")
            results.append({
                'activity': str(row.activity_type),
                'date': str(row.date),
            })
        return results

    def get_travel_data(self, start_date: datetime, end_date: datetime, person_uri: str) -> List[Dict[str, any]]:
        """Query travel bookings for a person within a date range."""
        # First, let's just get all travel bookings for the person
        query = self.prefixes + """
            SELECT DISTINCT ?place_name ?arrival_time
            WHERE {
                ?person rdf:type person:Person .
                ?person person:travelTo ?place .
                ?place travel:placeTime ?arrival_time .
                ?place travel:placeName ?place_name .
                FILTER(?arrival_time >= """ + f'"{start_date.isoformat()}"^^xsd:dateTime' + """ && 
                       ?arrival_time <= """ + f'"{end_date.isoformat()}"^^xsd:dateTime' + """)
            }
        """
        
        # print("\nDebug - Travel data query:")
        # print(query)
        
        results = []
        for row in self.graph.query(query):
            print(f"Found travel data: {row.place_name} {row.arrival_time}")
            results.append({
                'place_name': str(row.place_name),
                'arrival_time': str(row.arrival_time)
            })
        return results

    def get_combined_timeline(self, start_date: datetime, end_date: datetime, person_uri: str) -> List[Dict[str, any]]:
        """Get a combined timeline of health and travel events."""
        health_data = self.get_health_data(start_date, end_date, person_uri)
        travel_data = self.get_travel_data(start_date, end_date, person_uri)
        
        timeline = []
        
        # Add health events
        for data in health_data:
            timeline.append({
                'type': 'health',
                'timestamp': data['date'],
                'data': data
            })
            
        # Add travel events
        for data in travel_data:
            timeline.append({
                'type': 'travel',
                'timestamp': data['arrival_time'],
                'data': data
            })
            
        # Sort by date
        timeline.sort(key=lambda x: x['timestamp'])
        return timeline 