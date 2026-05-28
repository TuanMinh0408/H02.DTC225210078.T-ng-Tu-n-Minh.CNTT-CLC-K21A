import pandas as pd
import numpy as np
from pathlib import Path

def load_up_fall_sensor_data(csv_path):
    """
    Trích xuất dữ liệu cảm biến từ CSV của bộ UP-Fall (Tuần 6).
    Chúng ta lấy 6 trục: Belt Acc (X,Y,Z) và Wrist Acc (X,Y,Z).
    """
    try:
        # Skip 2 dòng đầu vì là header và units
        df = pd.read_csv(csv_path, header=None, skiprows=2)
        
        # Mapping các cột theo nghiên cứu UP-Fall:
        # Belt Accelerometer: Index 15, 16, 17
        # Wrist Accelerometer: Index 29, 30, 31
        # Activity Label: Index 44
        
        belt_acc = df.iloc[:, [15, 16, 17]].values # Shape: (N, 3)
        wrist_acc = df.iloc[:, [29, 30, 31]].values # Shape: (N, 3)
        
        # Kết hợp thành 6 features cảm biến
        sensor_features = np.hstack([belt_acc, wrist_acc]) # Shape: (N, 6)
        
        # Lấy nhãn (Activity)
        # UP-Fall: 1-5 là Falls, 6-11 là ADLs. 
        # Chúng ta chuyển về 0 (Bình thường) và 1 (Ngã)
        activity_ids = df.iloc[:, 44].values
        labels = np.where(activity_ids <= 5, 1, 0)
        
        return sensor_features, labels
        
    except Exception as e:
        print(f"Error loading {csv_path}: {e}")
        return None, None

if __name__ == "__main__":
    csv_file = "Subject1Activity1Trial1.csv"
    features, labels = load_up_fall_sensor_data(csv_file)
    if features is not None:
        print(f"Loaded {len(features)} samples from {csv_file}")
        print(f"Sensor features shape: {features.shape} (Belt + Wrist Acc)")
        print(f"Sample label (1=Fall, 0=ADL): {labels[0]}")
