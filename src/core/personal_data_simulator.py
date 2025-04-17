"""
Personal data simulator that combines data generation with ontology building.
"""

from datetime import datetime, timedelta
import random
from typing import Optional
from ..utils.data_simulator import PersonalDataSimulator
from .personal_ontology_builder import PersonalOntologyBuilder

class PersonalDataKnowledgeSimulator:
    def __init__(self, person_id: str, start_date: Optional[datetime] = None,
                 base_uri: str = "http://example.org/personal/"):
        """
        Initialize the personal data knowledge simulator.
        
        Args:
            person_id: Identifier for the person
            start_date: Starting date for the simulation
            base_uri: Base URI for the ontology
        """
        self.person_id = person_id
        self.data_simulator = PersonalDataSimulator(start_date)
        self.ontology_builder = PersonalOntologyBuilder(base_uri)
        self.travel_probability = 0.1  # 10% chance of travel booking per day
        
    def simulate_day(self) -> None:
        """Simulate one day of personal data and add it to the ontology."""
        # Generate and add health data
        health_data = self.data_simulator.generate_daily_health_data()
        self.ontology_builder.add_health_data(health_data, self.person_id)
        
        # Randomly generate travel bookings
        if random.random() < self.travel_probability:
            travel_data = self.data_simulator.generate_travel_booking()
            self.ontology_builder.add_travel_booking(travel_data, self.person_id)
        
        # Advance to next day
        self.data_simulator.advance_day()
    
    def simulate_period(self, days: int) -> None:
        """
        Simulate personal data for a specified number of days.
        
        Args:
            days: Number of days to simulate
        """
        for _ in range(days):
            self.simulate_day()
    
    def export_ontology(self, format: str = 'turtle', file_path: Optional[str] = None) -> Optional[str]:
        """
        Export the generated ontology.
        
        Args:
            format: Format to export (turtle, xml, n3, etc.)
            file_path: Path to save the exported ontology
            
        Returns:
            Optional[str]: String representation of the ontology if no file_path is provided
        """
        return self.ontology_builder.get_graph_manager().export_graph(format, file_path)
    
    def query_data(self, sparql_query: str) -> list:
        """
        Query the generated knowledge graph using SPARQL.
        
        Args:
            sparql_query: SPARQL query string
            
        Returns:
            list: Query results
        """
        return self.ontology_builder.get_graph_manager().query_graph(sparql_query) 