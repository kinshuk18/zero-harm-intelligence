import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_scada_data(days=5, interval_minutes=5):
    print("🚀 Initializing SCADA Data Synthesizer...")
    
    start_time = datetime.now() - timedelta(days=days)
    timestamps = [start_time + timedelta(minutes=i) for i in range(0, days * 24 * 60, interval_minutes)]
    
    df = pd.DataFrame({'timestamp': timestamps})
    
    # Baseline normal operations
    df['gas_pressure_psi'] = np.random.normal(50, 5, len(df))
    df['methane_ppm'] = np.random.normal(10, 2, len(df))
    df['temperature_c'] = np.random.normal(45, 3, len(df))
    
    # 0 = No active permit, 1 = Active Hot Work Permit
    df['hot_work_permit_active'] = np.random.choice([0, 1], size=len(df), p=[0.85, 0.15])
    
    # 0 = Normal, 1 = Confined Space Entry active
    df['confined_space_entry'] = np.random.choice([0, 1], size=len(df), p=[0.90, 0.10])

    # Injecting the "Compound Risk" Anomalies (The Hackathon Winner)
    # Scenario: Methane spike DURING an active Hot Work Permit
    anomaly_indices = np.random.choice(df.index, size=10, replace=False)
    for idx in anomaly_indices:
        df.loc[idx:idx+5, 'methane_ppm'] = np.random.uniform(80, 150, 6) # Dangerous spike
        df.loc[idx:idx+5, 'hot_work_permit_active'] = 1 # Co-occurring with hot work
        
    # Labeling the ground truth for your ML model (1 = Critical Compound Risk, 0 = Safe/Single Risk)
    df['critical_risk_flag'] = np.where(
        (df['methane_ppm'] > 50) & (df['hot_work_permit_active'] == 1), 1, 0
    )
    
    print(f"✅ Generated {len(df)} records. Embedded compound risk anomalies.")
    return df

if __name__ == "__main__":
    import os
    
    # Resolve absolute paths relative to this script location to prevent directory mismatches
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target_dir = os.path.join(base_dir, "data", "raw")
    
    # Automatically bootstrap data storage folders if missing
    os.makedirs(target_dir, exist_ok=True)
    
    dataset = generate_scada_data()
    save_path = os.path.join(target_dir, "simulated_scada_logs.csv")
    dataset.to_csv(save_path, index=False)
    print(f"💾 Data successfully saved to absolute path: {save_path}")