"""
Example script demonstrating how to query temporal health and travel data.
"""

from datetime import datetime, timedelta
import json
import os
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator
from src.core.query_manager import QueryManager

def main():
    # Set up date range for simulation
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Simulate last 30 days
    
    # Generate data
    print("Generating synthetic data...")
    person_id = "person123"
    
    # Initialize simulator with person ID and start date
    simulator = PersonalDataKnowledgeSimulator(person_id, start_date)
    
    # Simulate data for each day in the range
    current_date = start_date
    while current_date <= end_date:
        simulator.simulate_day()
        current_date += timedelta(days=1)

    simulator.export_ontology("turtle", "data/personal_data.ttl")
    
    # Initialize query manager with the generated graph
    query_manager = QueryManager(simulator.ontology_builder.get_graph_manager().graph)
    
    # Query health data
    print("\nQuerying health data...")
    health_data = query_manager.get_health_data(start_date, end_date, f"http://example.org/personal/person/{person_id}")

    
    # Query travel data
    print("\nQuerying travel data...")
    travel_data = query_manager.get_travel_data(start_date, end_date, f"http://example.org/personal/person/{person_id}")

    
    # Get combined timeline
    print("\nGetting combined timeline...")
    timeline = query_manager.get_combined_timeline(start_date, end_date, f"http://example.org/personal/person/{person_id}")
    print(f"Found {len(timeline)} total events")
    print("\nFirst 3 events in timeline:")
    for event in timeline[:3]:
        print(f"\nType: {event['type']}")
        print(f"Timestamp: {event['timestamp']}")
        print("Data:", json.dumps(event['data'], indent=2))
    
    # Save query results
    output = {
        'query_period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'person_id': person_id,
        'health_data': health_data,
        'travel_data': travel_data,
        'timeline': timeline
    }
    
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'query_results.json')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nQuery results saved to: {output_file}")

if __name__ == "__main__":
    main()