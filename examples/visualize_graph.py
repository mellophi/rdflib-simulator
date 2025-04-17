"""
Example script demonstrating knowledge graph visualization.
"""

from datetime import datetime, timedelta
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator
from src.visualization.visualizer import KnowledgeGraphVisualizer
from rdflib import URIRef

def main():
    # Initialize simulator and simulate 7 days of data
    print("Simulating 7 days of personal data...")
    simulator = PersonalDataKnowledgeSimulator()
    current_date = datetime.now()
    for _ in range(7):
        simulator.simulate_day(current_date)
        current_date += timedelta(days=1)
    
    # Initialize visualizer
    visualizer = KnowledgeGraphVisualizer(simulator.graph)
    
    # 1. Visualize the complete graph
    print("\nGenerating complete graph visualization...")
    visualizer.visualize_graph(output_path="data/complete_graph.png")
    
    # 2. Visualize health-related subgraph
    print("\nGenerating health metrics subgraph...")
    today = datetime.now().strftime("%Y-%m-%d")
    health_node = URIRef(f"http://example.org/personal/health/vitals_person123_{today}")
    visualizer.visualize_subgraph(
        central_node=health_node,
        output_path="data/health_subgraph.png"
    )
    
    # 3. Visualize travel-related subgraph
    print("\nGenerating travel booking subgraph...")
    # Find a booking node by checking for "booking_" in subject and "type" in predicate
    booking_node = None
    for s, p, o in simulator.graph:
        if "booking_" in str(s) and "type" in str(p):
            booking_node = s
            break
    
    if booking_node:
        visualizer.visualize_subgraph(
            central_node=booking_node,
            output_path="data/travel_subgraph.png"
        )
    else:
        print("No travel booking found in the graph.")
    
    print("\nVisualizations have been saved to the data directory:")
    print("1. data/complete_graph.png - Complete knowledge graph")
    print("2. data/health_subgraph.png - Health-related subgraph")
    print("3. data/travel_subgraph.png - Travel-related subgraph")

if __name__ == "__main__":
    main() 