"""
Example script demonstrating information gain analysis between health and travel data.
"""

from datetime import datetime, timedelta
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator
from src.analysis.information_gain import InformationGainAnalyzer
from rdflib import Graph
import copy

def simulate_scenario_1(simulator, start_date, days):
    """
    Scenario 1: Regular data addition
    - Daily data simulation with normal probability of travel bookings
    """
    health_gains = []
    travel_gains = []
    timestamps = []
    
    current_date = start_date
    prev_graph = None
    
    for day in range(days):
        # Create a copy of the current graph state
        if prev_graph is None:
            prev_graph = Graph()
        else:
            prev_graph = copy.deepcopy(simulator.ontology_builder.get_graph_manager().graph)
            
        # Simulate one day of data
        simulator.simulate_day()
            
        # Calculate information gain
        analyzer = InformationGainAnalyzer(simulator.ontology_builder.get_graph_manager().graph)
        
        health_gain = analyzer.calculate_information_gain(
            'health', prev_graph, simulator.ontology_builder.get_graph_manager().graph)
        travel_gain = analyzer.calculate_information_gain(
            'travel', prev_graph, simulator.ontology_builder.get_graph_manager().graph)
            
        health_gains.append(health_gain)
        travel_gains.append(travel_gain)
        timestamps.append(current_date.strftime('%Y-%m-%d'))
        
        current_date += timedelta(days=1)
        
    return health_gains, travel_gains, timestamps

def simulate_scenario_2(simulator, start_date, days):
    """
    Scenario 2: Burst data addition
    - Increased travel booking probability on certain days
    """
    health_gains = []
    travel_gains = []
    timestamps = []
    
    current_date = start_date
    prev_graph = None
    
    for day in range(days):
        # Create a copy of the current graph state
        if prev_graph is None:
            prev_graph = Graph()
        else:
            prev_graph = copy.deepcopy(simulator.ontology_builder.get_graph_manager().graph)
            
        # On weekly basis, increase travel probability
        if day % 7 == 0:
            original_prob = simulator.travel_probability
            simulator.travel_probability = 0.8  # 80% chance of travel booking
            simulator.simulate_day()
            simulator.travel_probability = original_prob
        else:
            simulator.simulate_day()
                
        # Calculate information gain
        analyzer = InformationGainAnalyzer(simulator.ontology_builder.get_graph_manager().graph)
        
        health_gain = analyzer.calculate_information_gain(
            'health', prev_graph, simulator.ontology_builder.get_graph_manager().graph)
        travel_gain = analyzer.calculate_information_gain(
            'travel', prev_graph, simulator.ontology_builder.get_graph_manager().graph)
            
        health_gains.append(health_gain)
        travel_gains.append(travel_gain)
        timestamps.append(current_date.strftime('%Y-%m-%d'))
        
        current_date += timedelta(days=1)
        
    return health_gains, travel_gains, timestamps

def main():
    # Initialize simulator with a person ID and start date
    person_id = "person123"
    start_date = datetime.now()
    simulator = PersonalDataKnowledgeSimulator(person_id, start_date)
    days_to_simulate = 14
    
    print("Simulating Scenario 1: Regular data addition")
    health_gains1, travel_gains1, timestamps1 = simulate_scenario_1(
        simulator, start_date, days_to_simulate)
    
    # Reset simulator for scenario 2
    simulator = PersonalDataKnowledgeSimulator(person_id, start_date)
    
    print("Simulating Scenario 2: Burst data addition")
    health_gains2, travel_gains2, timestamps2 = simulate_scenario_2(
        simulator, start_date, days_to_simulate)
    
    # Create analyzer for plotting
    analyzer = InformationGainAnalyzer(simulator.ontology_builder.get_graph_manager().graph)
    
    # Plot results
    print("\nGenerating plots...")
    
    # Plot Scenario 1
    analyzer.plot_information_gain_comparison(
        health_gains1, travel_gains1, timestamps1,
        output_file="data/information_gain_scenario1.png"
    )
    
    # Plot Scenario 2
    analyzer.plot_information_gain_comparison(
        health_gains2, travel_gains2, timestamps2,
        output_file="data/information_gain_scenario2.png"
    )
    
    print("\nAnalysis complete! Plots have been saved to:")
    print("1. data/information_gain_scenario1.png - Regular data addition")
    print("2. data/information_gain_scenario2.png - Burst data addition")

if __name__ == "__main__":
    main() 