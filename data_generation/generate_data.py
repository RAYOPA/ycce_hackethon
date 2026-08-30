import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

def generate_synthetic_data(num_personnel=1000, days=90):
    np.random.seed(42)
    random.seed(42)
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for p_id in range(1, num_personnel + 1):
        personnel_id = f"P{p_id:04d}"
        
        # Individual baselines
        base_sleep = np.random.normal(7.5, 0.5)
        base_mood = np.random.normal(4.0, 0.5)
        base_workload = np.random.normal(2.5, 0.5)
        
        # Determine if this person has a "stress event" during the period
        has_stress_event = random.random() < 0.2  # 20% chance of a stress event
        stress_start_day = random.randint(20, 60) if has_stress_event else -1
        stress_duration = random.randint(7, 21)
        
        deployment_duration = random.randint(1, 24) # months
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Default values (normal day)
            sleep = np.clip(np.random.normal(base_sleep, 0.5), 2, 10)
            mood = np.clip(np.random.normal(base_mood, 0.5), 1, 5)
            workload = np.clip(np.random.normal(base_workload, 0.5), 1, 5)
            night_duty = 1 if random.random() < 0.1 else 0
            leave_gap = day + random.randint(10, 100) # Days since last leave
            training_load = np.random.normal(2.0, 0.5)
            
            consecutive_duty = day % 7 + 1 if random.random() > 0.1 else 0 # simple approximation
            
            # Apply stress event modifications
            is_stress_period = 0
            if has_stress_event and stress_start_day <= day < stress_start_day + stress_duration:
                is_stress_period = 1
                sleep = np.clip(np.random.normal(base_sleep - 2.0, 0.5), 2, 10)
                mood = np.clip(np.random.normal(base_mood - 1.5, 0.5), 1, 5)
                workload = np.clip(np.random.normal(base_workload + 1.5, 0.5), 1, 5)
                night_duty = 1 if random.random() < 0.4 else 0
                consecutive_duty += 5 # simulate long duty
            
            # Self-reported stress (correlated with other negative factors)
            # Higher workload, lower sleep, lower mood -> higher stress
            stress_score = (5 - mood) * 0.3 + (10 - sleep) * 0.2 + workload * 0.3 + (night_duty * 0.1)
            stress_score = np.clip(stress_score + np.random.normal(0, 0.2), 1, 5)
            
            # "Target" risk flag for training (1 if high risk period, 0 otherwise)
            # This is synthetic ground truth. We define high risk if sleep is low, mood is low, workload is high for a bit
            risk_flag = 1 if is_stress_period else 0
            if stress_score > 4.0:
                 risk_flag = 1
            
            data.append({
                'personnel_id': personnel_id,
                'date': current_date.strftime('%Y-%m-%d'),
                'deployment_duration_months': deployment_duration,
                'duty_duration_hrs': np.random.normal(8, 1) if not is_stress_period else np.random.normal(12, 2),
                'consecutive_duty_days': consecutive_duty,
                'night_duty': night_duty,
                'leave_gap_days': leave_gap,
                'training_load': np.clip(training_load, 1, 5),
                'sleep_hours': round(sleep, 1),
                'mood_score': round(mood, 1),
                'workload_perception': round(workload, 1),
                'self_reported_stress': round(stress_score, 1),
                'risk_flag': risk_flag
            })
            
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    print("Generating synthetic data...")
    df = generate_synthetic_data(num_personnel=1000, days=90)
    output_path = "synthetic_welfare_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Data generated successfully. Shape: {df.shape}")
    print(f"Saved to {output_path}")
    print(df.head())
