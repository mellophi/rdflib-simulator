"""
Example script to identify baseline drift in health vitals over time.
"""

from datetime import datetime, timedelta
import numpy as np
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from sklearn.metrics import roc_curve, auc
import json
import os
import random

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

def generate_lazy_health_data(simulator):
    """Generate health data with a lazy pattern (reduced activity)."""
    data = simulator.data_simulator.generate_daily_health_data()
    
    # Modify the data to show a lazy pattern
    data['steps'] = int(data['steps'] * 0.6)  # 40% reduction in steps
    data['heart_rate']['average'] = int(data['heart_rate']['average'] * 0.9)  # 10% reduction in heart rate
    data['calories_burned'] = int(data['calories_burned'] * 0.7)  # 30% reduction in calories
    data['sleep']['duration'] *= 1.2  # 20% increase in sleep duration
    
    return data

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

def plot_drift_heatmap(data, output_file: str):
    """Plot heatmap showing drift patterns across all persons."""
    plt.figure(figsize=(12, 8))
    
    # Plot ground truth
    plt.subplot(2, 1, 1)
    plt.imshow(data[:, 0, :], aspect='auto', cmap='YlOrRd')
    plt.title('Ground Truth Drift Patterns')
    plt.xlabel('Week')
    plt.ylabel('Person ID')
    plt.colorbar(label='Drift Present')
    
    # Plot detected changes
    plt.subplot(2, 1, 2)
    plt.imshow(data[:, 1, :], aspect='auto', cmap='YlOrRd')
    plt.title('Detected Drift Patterns')
    plt.xlabel('Week')
    plt.ylabel('Person ID')
    plt.colorbar(label='Change Detected')
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_metric_distributions(all_metrics: List[Dict], drift_starts: List[int], output_file: str):
    """Plot distribution of metrics before and after drift."""
    # Collect metrics before and after drift
    before_hr = []
    after_hr = []
    before_bp = []
    after_bp = []
    before_sleep = []
    after_sleep = []
    
    for person_idx, metrics in enumerate(all_metrics):
        drift_day = drift_starts[person_idx]
        for day, data in enumerate(metrics):
            if day < drift_day:
                before_hr.append(data['heart_rate']['average'])
                before_bp.append(data['blood_pressure']['systolic'])
                before_sleep.append(data['sleep']['duration'])
            else:
                after_hr.append(data['heart_rate']['average'])
                after_bp.append(data['blood_pressure']['systolic'])
                after_sleep.append(data['sleep']['duration'])
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Heart Rate Distribution
    axes[0].hist(before_hr, alpha=0.5, label='Before Drift', bins=20)
    axes[0].hist(after_hr, alpha=0.5, label='After Drift', bins=20)
    axes[0].set_title('Heart Rate Distribution')
    axes[0].set_xlabel('Heart Rate (bpm)')
    axes[0].set_ylabel('Frequency')
    axes[0].legend()
    
    # Blood Pressure Distribution
    axes[1].hist(before_bp, alpha=0.5, label='Before Drift', bins=20)
    axes[1].hist(after_bp, alpha=0.5, label='After Drift', bins=20)
    axes[1].set_title('Blood Pressure Distribution')
    axes[1].set_xlabel('Systolic BP (mmHg)')
    axes[1].set_ylabel('Frequency')
    axes[1].legend()
    
    # Sleep Duration Distribution
    axes[2].hist(before_sleep, alpha=0.5, label='Before Drift', bins=20)
    axes[2].hist(after_sleep, alpha=0.5, label='After Drift', bins=20)
    axes[2].set_title('Sleep Duration Distribution')
    axes[2].set_xlabel('Sleep Duration (hours)')
    axes[2].set_ylabel('Frequency')
    axes[2].legend()
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def plot_confusion_matrix(y_true, y_pred, output_file: str):
    """Plot confusion matrix for drift detection."""
    from sklearn.metrics import confusion_matrix
    import seaborn as sns
    
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig(output_file)
    plt.close()

def plot_average_trends(all_metrics: List[Dict], drift_starts: List[int], output_file: str):
    """Plot average metric trends across all persons."""
    max_days = max(len(metrics) for metrics in all_metrics)
    
    # Initialize arrays for average values
    avg_hr = np.zeros(max_days)
    avg_bp = np.zeros(max_days)
    avg_sleep = np.zeros(max_days)
    counts = np.zeros(max_days)
    
    # Collect daily averages
    for metrics in all_metrics:
        for day, data in enumerate(metrics):
            avg_hr[day] += data['heart_rate']['average']
            avg_bp[day] += data['blood_pressure']['systolic']
            avg_sleep[day] += data['sleep']['duration']
            counts[day] += 1
    
    # Calculate averages
    avg_hr /= counts
    avg_bp /= counts
    avg_sleep /= counts
    
    # Plot trends
    plt.figure(figsize=(12, 8))
    
    plt.subplot(3, 1, 1)
    plt.plot(avg_hr, label='Heart Rate')
    plt.title('Average Heart Rate Trend')
    plt.xlabel('Day')
    plt.ylabel('BPM')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 1, 2)
    plt.plot(avg_bp, label='Blood Pressure')
    plt.title('Average Blood Pressure Trend')
    plt.xlabel('Day')
    plt.ylabel('mmHg')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(3, 1, 3)
    plt.plot(avg_sleep, label='Sleep Duration')
    plt.title('Average Sleep Duration Trend')
    plt.xlabel('Day')
    plt.ylabel('Hours')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def main():
    persons_count = 50
    days_count = 30
    weeks_count = days_count // 7
    drift_insertion_range = (1, days_count)
    data = np.zeros((persons_count, 2, weeks_count))
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    all_health_data = []
    drift_start_days = []
    
    for id in range(persons_count):
        # Initialize simulator
        person_id = f"person{id}"
        start_date = datetime.now()
        simulator = PersonalDataKnowledgeSimulator(person_id, start_date)
        
        # Simulate 30 days of data
        print(f"Simulating {days_count} days of health data for {person_id}...")
        health_data = []

        # Simulate ground truth drift
        gt_drift_start_date = random.randint(*drift_insertion_range)
        drift_start_days.append(gt_drift_start_date)
        gt_drift_weeks = gt_drift_start_date // 7
        if gt_drift_weeks > 0 and gt_drift_weeks < weeks_count:
            data[id, 0, gt_drift_weeks:] = 1  # Mark weeks after drift starts
        print(f"Ground truth drift starts at day {gt_drift_start_date} (week {gt_drift_weeks})")
        
        for day in range(days_count):
            data_type = simulator.simulate_day()
            # Extract health data from the simulator
            current_date = simulator.data_simulator.current_date
            if day >= gt_drift_start_date:
                health_metrics = generate_lazy_health_data(simulator)
            else:
                health_metrics = simulator.data_simulator.generate_daily_health_data()
            health_data.append(health_metrics)
        
        all_health_data.append(health_data)
        
        # Calculate weekly averages
        heart_rate_avgs, bp_avgs, sleep_avgs = calculate_weekly_averages(health_data)
        
        # Detect significant changes
        hr_changes = detect_significant_changes(heart_rate_avgs)
        bp_changes = detect_significant_changes(bp_avgs)
        sleep_changes = detect_significant_changes(sleep_avgs)
        
        # Create prediction array
        pred_changes = np.zeros(weeks_count)
        # Mark weeks where any metric showed significant change
        for week in set(hr_changes + bp_changes + sleep_changes):
            if week < weeks_count:  # Ensure we don't exceed array bounds
                pred_changes[week] = 1
        data[id, 1, :] = pred_changes

        # Plot individual results
        if id == 0:  # Only plot for the first person as an example
            weeks = list(range(len(heart_rate_avgs)))
            weekly_data = [heart_rate_avgs, bp_avgs, sleep_avgs]
            significant_changes = [hr_changes, bp_changes, sleep_changes]
            plot_health_trends(weekly_data, weeks, significant_changes, 
                             os.path.join(output_dir, f'health_baseline_drift_{person_id}.png'))
    
    # Calculate ROC curve
    y_true = data[:, 0, :].flatten()
    y_pred = data[:, 1, :].flatten()
    
    # Calculate ROC curve points
    fpr, tpr, _ = roc_curve(y_true, y_pred)
    roc_auc = auc(fpr, tpr)
    
    # Generate additional visualizations
    plot_drift_heatmap(data, os.path.join(output_dir, 'drift_heatmap.png'))
    plot_metric_distributions(all_health_data, drift_start_days, 
                            os.path.join(output_dir, 'metric_distributions.png'))
    plot_confusion_matrix(y_true, y_pred, 
                         os.path.join(output_dir, 'confusion_matrix.png'))
    plot_average_trends(all_health_data, drift_start_days,
                       os.path.join(output_dir, 'average_trends.png'))
    
    # Plot ROC curve
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")
    
    # Save ROC curve plot
    roc_output_file = os.path.join(output_dir, 'health_baseline_drift_roc.png')
    plt.savefig(roc_output_file)
    plt.close()
    
    print(f"\nAnalysis complete! Plots have been saved to:")
    print(f"1. Individual plots: {output_dir}/health_baseline_drift_person*.png")
    print(f"2. ROC curve: {roc_output_file}")
    print(f"3. Drift heatmap: {output_dir}/drift_heatmap.png")
    print(f"4. Metric distributions: {output_dir}/metric_distributions.png")
    print(f"5. Confusion matrix: {output_dir}/confusion_matrix.png")
    print(f"6. Average trends: {output_dir}/average_trends.png")
    print(f"\nROC AUC Score: {roc_auc:.3f}")

if __name__ == "__main__":
    main()

