import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path

class MultimodalFusionDataset(Dataset):
    def __init__(self, pose_data_path, sensor_data, labels, seq_length=30):
        """
        Dataset kết hợp Pose (34) + Sensors (6) = 40 features (Tuần 6).
        pose_data: (N_frames, 17, 3) 
        sensor_data: (N_frames, 6)
        """
        # Load pose data
        self.pose_data = np.load(pose_data_path)
        # Bỏ cột confidence, chỉ lấy x, y -> (N, 17, 2)
        self.pose_data = self.pose_data[:, :, :2].reshape(len(self.pose_data), -1)
        
        self.sensor_data = sensor_data
        self.labels = labels
        self.seq_length = seq_length
        
        # Đồng bộ hóa chiều dài (Alignment)
        min_len = min(len(self.pose_data), len(self.sensor_data))
        self.pose_data = self.pose_data[:min_len]
        self.sensor_data = self.sensor_data[:min_len]
        self.labels = self.labels[:min_len]
        
        # Kết hợp thành 40 features
        self.combined_data = np.hstack([self.pose_data, self.sensor_data])
        
    def __len__(self):
        return len(self.combined_data) - self.seq_length
        
    def __getitem__(self, idx):
        # Lấy một cửa sổ trượt (sliding window)
        x = self.combined_data[idx : idx + self.seq_length]
        y = self.labels[idx + self.seq_length - 1] # Nhãn của frame cuối trong chuỗi
        
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.long)

if __name__ == "__main__":
    from multimodal_pipeline import load_up_fall_sensor_data
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    pose_path = BASE_DIR / "data" / "processed" / "sample_1_kp.npy"
    csv_path = BASE_DIR / "Subject1Activity1Trial1.csv"
    
    if pose_path.exists() and csv_path.exists():
        sensor_feat, labels = load_up_fall_sensor_data(csv_path)
        dataset = MultimodalFusionDataset(pose_path, sensor_feat, labels)
        dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
        
        for batch_x, batch_y in dataloader:
            print(f"Batch X shape: {batch_x.shape} (Batch, Seq, 40 Features)")
            print(f"Batch Y shape: {batch_y.shape}")
            break
