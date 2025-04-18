"""
Example script demonstrating information gain analysis between health and travel data.
"""

from datetime import datetime, timedelta
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator, DataType
from src.analysis.information_gain import InformationGainAnalyzer
from rdflib import Graph
import copy
import math
import random
import matplotlib.pyplot as plt

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

def simulate_scenario_3(simulator, start_date, days):
    """
    Scenario 3: Information gain trade-off between travel and T
    - As travel instances increase, their information gain reduces
    - T instances start with low probability but increase over time with the occurance of travel instances
        (formula to increase t_probability: t_W = (0.2 * travel_instances))
    - Shows inflection point where T information gain overtakes travel
    """
    health_gains = []
    travel_gains = []
    t_gains = []
    h_gains = []
    total_gains = []
    timestamps = []
    
    current_date = start_date
    prev_graph = None

    travel_probability = 0.05
    health_probability = 0.1
    
    simulator.travel_probability = travel_probability
    simulator.health_probability = health_probability
    
    # Initialize T probability low
    t_probability = 0.001
    h_probability = 0.001
    t_W = 0
    h_W = 0
    t_instances = 10
    h_instances = 5
    t_gain = 0.0
    h_gain = 0.0
    travel_instances = 0
    health_instances = 0
    
    for day in range(days):
        # Create a copy of the current graph state
        if prev_graph is None:
            prev_graph = Graph()
        else:
            prev_graph = copy.deepcopy(simulator.ontology_builder.get_graph_manager().graph)
            
        # Simulate travel with diminishing returns
        
        data_type = simulator.simulate_day()
        travel_instances += 1 if data_type == DataType.HEALTH_AND_TRAVEL or data_type == DataType.TRAVEL_ONLY else 0
        health_instances += 1 if data_type == DataType.HEALTH_AND_TRAVEL or data_type == DataType.HEALTH_ONLY else 0

        # Increase T probability based on travel instances
        t_W = (0.2 * travel_instances)
        h_W = (0.2 * health_instances)
                
        # Calculate information gain
        analyzer = InformationGainAnalyzer(simulator.ontology_builder.get_graph_manager().graph)
        
        travel_gain = analyzer.calculate_information_gain(
            'travel', prev_graph, simulator.ontology_builder.get_graph_manager().graph)
        health_gain = analyzer.calculate_information_gain(
            'health', prev_graph, simulator.ontology_builder.get_graph_manager().graph)
        t_gain -= t_W * t_instances * t_probability *  math.log2(t_probability) 
        h_gain -= h_W * h_instances * h_probability *  math.log2(h_probability) 

        travel_gains.append(travel_gain)
        health_gains.append(health_gain)
        t_gains.append(t_gain)
        h_gains.append(h_gain)
        total_gains.append(travel_gain + health_gain + t_gain + h_gain)
        timestamps.append(current_date.strftime('%Y-%m-%d'))
        
        current_date += timedelta(days=1)
        
        
    return travel_gains, t_gains, health_gains, h_gains, total_gains, timestamps




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
    
    # Reset simulator for scenario 3
    simulator = PersonalDataKnowledgeSimulator(person_id, start_date)
    
    print("Simulating Scenario 3: Information gain trade-off")
    travel_gains3, t_gains3, health_gains3, h_gains3, total_gains3, timestamps3 = simulate_scenario_3(
        simulator, start_date, 50)
    
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
    
    # Plot Scenario 3 (using matplotlib directly as it has different metrics)
    plt.figure(figsize=(12, 6))
    x = range(len(timestamps3))
    plt.plot(x, travel_gains3, label='Travel Information Gain', color='#FF6B6B')
    plt.plot(x, health_gains3, label='Health Information Gain', color='#4ECDC4') 
    plt.plot(x, t_gains3, label='T Information Gain', color='#45B7D1')
    plt.plot(x, h_gains3, label='H Information Gain', color='#96CEB4')
    plt.plot(x, total_gains3, label='Total Information Gain', color='#FFD93D', linewidth=2)
    plt.xlabel('Time (Days)')
    plt.ylabel('Information Gain')
    plt.title('Information Gain Trade-off')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('data/information_gain_scenario3.png')
    plt.close()
    
    print("\nAnalysis complete! Plots have been saved to:")
    print("1. data/information_gain_scenario1.png - Regular data addition")
    print("2. data/information_gain_scenario2.png - Burst data addition")
    print("3. data/information_gain_scenario3.png - Information gain trade-off")

if __name__ == "__main__":
    main() 