"""
Example script to identify baseline drift in health vitals over time and output combined RDF graph.
"""

from datetime import datetime, timedelta
import numpy as np
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from sklearn.metrics import roc_curve, auc, accuracy_score, precision_score, recall_score, f1_score
import json
import os
import random
from rdflib import Graph, Namespace, RDF, RDFS, XSD, OWL

def calculate_weekly_averages(health_data: List[Dict]) -> Tuple[List[float], List[float], List[float]]:
    """
    Calculate weekly averages for heart rate, blood pressure, and sleep duration.
    
    Args:
        health_data: List of daily health metrics
        
    Returns:
        Tuple of lists containing weekly averages for heart rate, blood pressure, and sleep
    """
    weekly_heart_rates = []
    weekly_blood_pressure = []
    weekly_sleep = []
    
    # Group data by weeks
    week_data = []
    current_week = []
    
    for day_data in health_data:
        current_week.append(day_data)
        if len(current_week) == 7:
            week_data.append(current_week)
            current_week = []
    
    # Add remaining days if any
    if current_week:
        week_data.append(current_week)
    # Calculate weekly averages
    for week in week_data:
        # Heart rate
        avg_heart_rate = np.mean([day['heart_rate']['average'] for day in week])
        weekly_heart_rates.append(avg_heart_rate)
        
        # Blood pressure (systolic)
        avg_bp = np.mean([day['blood_pressure']['systolic'] for day in week])
        weekly_blood_pressure.append(avg_bp)
        
        # Sleep duration
        avg_sleep = np.mean([day['sleep']['duration'] for day in week])
        weekly_sleep.append(avg_sleep)
    
    return weekly_heart_rates, weekly_blood_pressure, weekly_sleep

def detect_significant_changes(weekly_data: List[float], threshold: float = None) -> Tuple[List[int], List[float]]:
    """
    Detect weeks with significant changes compared to the previous week using adaptive thresholding.
    
    Args:
        weekly_data: List of weekly averages
        threshold: Optional override for the adaptive threshold
        
    Returns:
        Tuple of (list of week indices where significant changes occurred, list of percentage changes)
    """
    significant_changes = []
    percent_changes = [0.0]  # First week has no change

    print(len(weekly_data))
    
    if len(weekly_data) < 2:
        return significant_changes, percent_changes
    
    # Calculate rolling statistics
    window = min(3, len(weekly_data))
    rolling_mean = np.convolve(weekly_data, np.ones(window)/window, mode='valid')
    rolling_std = np.array([np.std(weekly_data[max(0, i-window):i+1]) 
                           for i in range(len(weekly_data))])
    
    # Compute adaptive threshold if not provided
    if threshold is None:
        # Use mean + 2*std of the first few weeks as baseline
        baseline_weeks = min(3, len(weekly_data))
        baseline_data = weekly_data[:baseline_weeks]
        threshold = np.mean(baseline_data) + 2 * np.std(baseline_data)
    
    for i in range(1, len(weekly_data)):
        prev_week = weekly_data[i-1]
        current_week = weekly_data[i]
        
        # Calculate percentage change
        percent_change = abs(current_week - prev_week) / prev_week
        percent_changes.append(percent_change)
        
        # Check for significant changes using multiple criteria
        is_significant = False
        
        # Criterion 1: Percentage change exceeds threshold
        if percent_change > threshold:
            is_significant = True
            
        # Criterion 2: Value outside rolling mean ± 2*std
        if i >= window and abs(current_week - rolling_mean[i-window]) > 2 * rolling_std[i]:
            is_significant = True
            
        # Criterion 3: Consistent trend direction over window
        if i >= window:
            trend = all(np.diff(weekly_data[i-window:i+1]) > 0) or \
                   all(np.diff(weekly_data[i-window:i+1]) < 0)
            if trend and percent_change > threshold/2:  # Lower threshold for consistent trends
                is_significant = True
        
        if is_significant:
            significant_changes.append(i)
    
    return significant_changes, percent_changes

def generate_lazy_health_data(simulator):
    """Generate health data with a lazy pattern (reduced activity)."""
    data = simulator.data_simulator.generate_daily_health_data()
    
    # Modify the data to show a lazy pattern
    data['steps'] = int(data['steps'] * 0.6)  # 40% reduction in steps
    data['heart_rate']['average'] = int(data['heart_rate']['average'] * 0.9)  # 10% reduction in heart rate
    data['calories_burned'] = int(data['calories_burned'] * 0.7)  # 30% reduction in calories
    data['sleep']['duration'] *= 1.2  # 20% increase in sleep duration
    
    return data

def main():
    persons_count = 50
    days_count = 30
    weeks_count = days_count // 7 + 1
    drift_insertion_range = (1, days_count)
    data = np.zeros((persons_count, 2, weeks_count))
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize combined graph with proper namespaces
    combined_graph = Graph()
    
    # Bind common namespaces
    HEALTH = Namespace("http://example.org/health#")
    PERSON = Namespace("http://example.org/person#")
    TRAVEL = Namespace("http://example.org/travel#")
    
    combined_graph.bind("health", HEALTH)
    combined_graph.bind("person", PERSON)
    combined_graph.bind("travel", TRAVEL)
    combined_graph.bind("rdf", RDF)
    combined_graph.bind("rdfs", RDFS)
    combined_graph.bind("xsd", XSD)
    combined_graph.bind("owl", OWL)
    
    all_health_data = []
    drift_start_days = []
    all_percent_changes = []
    
    for id in range(persons_count):
        # Initialize simulator
        person_id = f"person{id}"
        start_date = datetime.now()
        simulator = PersonalDataKnowledgeSimulator(person_id, start_date)
        
        # Simulate 30 days of data
        health_data = []

        # Simulate ground truth drift
        gt_drift_start_date = random.randint(*drift_insertion_range)
        drift_start_days.append(gt_drift_start_date)
        gt_drift_weeks = gt_drift_start_date // 7
        if gt_drift_weeks > 0 and gt_drift_weeks < weeks_count:
            data[id, 0, gt_drift_weeks:] = 1  # Mark weeks after drift starts
        
        for day in range(days_count):
            data_type = simulator.simulate_day()
            # Extract health data from the simulator
            current_date = simulator.data_simulator.current_date
            if day >= gt_drift_start_date:
                health_metrics = generate_lazy_health_data(simulator)
            else:
                health_metrics = simulator.data_simulator.generate_daily_health_data()
            simulator.ontology_builder.add_health_data(health_metrics, person_id)
            health_data.append(health_metrics)
        
        # Merge individual graph into combined graph
        individual_graph = simulator.ontology_builder.gm.graph
        
        # Copy namespace bindings from individual graph if they don't exist
        for prefix, namespace in individual_graph.namespaces():
            if prefix not in combined_graph.namespaces():
                combined_graph.bind(prefix, namespace)
        
        combined_graph += individual_graph
        
        all_health_data.append(health_data)
        
        # Calculate weekly averages and detect changes
        heart_rate_avgs, bp_avgs, sleep_avgs = calculate_weekly_averages(health_data)
        hr_changes, hr_pct = detect_significant_changes(heart_rate_avgs)
        bp_changes, bp_pct = detect_significant_changes(bp_avgs)
        sleep_changes, sleep_pct = detect_significant_changes(sleep_avgs)
        
        # Process metrics and changes
        avg_pct_changes = [np.mean([hr_pct[i], bp_pct[i], sleep_pct[i]]) for i in range(len(hr_pct))]
        hr_std = np.std(heart_rate_avgs)
        bp_std = np.std(bp_avgs)
        sleep_std = np.std(sleep_avgs)
        
        normalized_changes = [np.mean([
            hr_pct[i]/hr_std if hr_std > 0 else 0,
            bp_pct[i]/bp_std if bp_std > 0 else 0,
            sleep_pct[i]/sleep_std if sleep_std > 0 else 0
        ]) for i in range(len(hr_pct))]
        
        combined_changes = [0.7 * avg_pct_changes[i] + 0.3 * normalized_changes[i] 
                          for i in range(len(avg_pct_changes))]
        
        all_percent_changes.extend(combined_changes)
        
        # Create prediction array
        pred_changes = np.zeros(weeks_count)
        for week in set(hr_changes + bp_changes + sleep_changes):
            if week < weeks_count:
                pred_changes[week] = 1
        data[id, 1, :] = pred_changes

    # Save combined graph to TTL file
    ttl_output = os.path.join(output_dir, 'combined_health_data.ttl')
    combined_graph.serialize(destination=ttl_output, format='turtle')
    
    print(f"\nAnalysis complete! Combined RDF graph saved to: {ttl_output}")

if __name__ == "__main__":
    main()
