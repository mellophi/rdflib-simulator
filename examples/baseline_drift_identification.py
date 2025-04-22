"""
Example script to identify baseline drift in health vitals over time.
"""

from datetime import datetime, timedelta
import numpy as np
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import json
import os

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

def detect_significant_changes(weekly_data: List[float], threshold: float = 0.1) -> List[int]:
    """
    Detect weeks with significant changes compared to the previous week.
    
    Args:
        weekly_data: List of weekly averages
        threshold: Percentage change threshold to consider significant
        
    Returns:
        List of week indices where significant changes occurred
    """
    significant_changes = []
    
    for i in range(1, len(weekly_data)):
        prev_week = weekly_data[i-1]
        current_week = weekly_data[i]
        
        # Calculate percentage change
        percent_change = abs(current_week - prev_week) / prev_week
        
        if percent_change > threshold:
            significant_changes.append(i)
    
    return significant_changes

def plot_health_trends(weekly_data: List[List[float]], weeks: List[int], 
                      significant_changes: List[List[int]], output_file: str):
    """Plot health metrics trends with highlighted significant changes."""
    metrics = ['Heart Rate', 'Blood Pressure', 'Sleep Duration']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    plt.figure(figsize=(15, 10))
    
    for idx, (data, metric, color) in enumerate(zip(weekly_data, metrics, colors)):
        plt.subplot(3, 1, idx + 1)
        plt.plot(weeks, data, marker='o', color=color, label=metric)
        
        # Highlight significant changes
        for change_week in significant_changes[idx]:
            plt.axvline(x=change_week, color='red', linestyle='--', alpha=0.3)
            plt.scatter([change_week], [data[change_week]], 
                       color='red', s=100, zorder=5)
            
            # Add annotation
            plt.annotate(f'Significant change\nWeek {change_week + 1}',
                        xy=(change_week, data[change_week]),
                        xytext=(10, 10), textcoords='offset points',
                        ha='left', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.3),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        plt.title(f'{metric} Weekly Average')
        plt.xlabel('Week')
        plt.ylabel('Average Value')
        plt.grid(True, alpha=0.3)
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def main():
    # Initialize simulator
    person_id = "person123"
    start_date = datetime.now()
    simulator = PersonalDataKnowledgeSimulator(person_id, start_date)
    
    # Simulate 30 days of data
    print("Simulating 30 days of health data...")
    health_data = []
    
    for _ in range(30):
        data_type = simulator.simulate_day()
        # Extract health data from the simulator
        current_date = simulator.data_simulator.current_date
        health_metrics = simulator.data_simulator.generate_daily_health_data()
        health_data.append(health_metrics)
    
    # Calculate weekly averages
    heart_rate_avgs, bp_avgs, sleep_avgs = calculate_weekly_averages(health_data)
    
    # Detect significant changes
    hr_changes = detect_significant_changes(heart_rate_avgs)
    bp_changes = detect_significant_changes(bp_avgs)
    sleep_changes = detect_significant_changes(sleep_avgs)
    
    # Plot results
    weeks = list(range(len(heart_rate_avgs)))
    weekly_data = [heart_rate_avgs, bp_avgs, sleep_avgs]
    significant_changes = [hr_changes, bp_changes, sleep_changes]
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'health_baseline_drift.png')
    
    plot_health_trends(weekly_data, weeks, significant_changes, output_file)
    
    # Print summary
    print("\nAnalysis Summary:")
    print(f"Total days analyzed: 30")
    print(f"Number of weeks: {len(heart_rate_avgs)}")
    print("\nSignificant Changes Detected:")
    print(f"Heart Rate: {len(hr_changes)} changes in weeks {[w+1 for w in hr_changes]}")
    print(f"Blood Pressure: {len(bp_changes)} changes in weeks {[w+1 for w in bp_changes]}")
    print(f"Sleep Duration: {len(sleep_changes)} changes in weeks {[w+1 for w in sleep_changes]}")
    
    print(f"\nPlot saved to: {output_file}")

if __name__ == "__main__":
    main()

