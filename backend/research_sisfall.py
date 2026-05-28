import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_sisfall_file(file_path, output_dir):
    """
    Phân tích file dữ liệu SisFall và vẽ biểu đồ Magnitude.
    SisFall format: Col 1-3 (ADXL345 Acc), Col 4-6 (ITG3200 Gyro), Col 7-9 (MMA8451 Acc)
    """
    file_path = Path(file_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Đọc dữ liệu
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        data = []
        for line in lines:
            # Loại bỏ dấu chấm phẩy và tách bằng dấu phẩy
            clean_line = line.strip().replace(';', '')
            if not clean_line: continue
            vals = [int(v) for v in clean_line.split(',')]
            data.append(vals)
        
        data = np.array(data)
        
        # Chúng ta dùng dữ liệu từ cảm biến MMA8451 (cột 7, 8, 9) - chỉ số 6, 7, 8
        # Các giá trị là raw bits. Cần tính Magnitude (SVM)
        acc_x = data[:, 6]
        acc_y = data[:, 7]
        acc_z = data[:, 8]
        
        svm = np.sqrt(acc_x**2 + acc_y**2 + acc_z**2)
        
        # Vẽ biểu đồ
        plt.figure(figsize=(12, 6))
        plt.plot(svm, label='Signal Vector Magnitude (SVM)', color='#3b82f6', linewidth=1)
        
        # Tiêu đề và nhãn
        file_name = file_path.name
        is_fall = file_name.startswith('F')
        plt.title(f"SisFall Data Analysis - {file_name} ({'FALL' if is_fall else 'ADL'})")
        plt.xlabel('Sample Index')
        plt.ylabel('Magnitude (Raw bits)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Lưu biểu đồ
        save_path = output_dir / f"{file_path.stem}_plot.png"
        plt.savefig(save_path, dpi=150)
        plt.close()
        
        print(f"Successfully analyzed {file_name} and saved plot to {save_path}")
        return str(save_path)
        
    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return None

if __name__ == "__main__":
    # Ví dụ chạy thử với 1 file trong SA01
    BASE_DIR = Path(__file__).resolve().parent.parent
    SISFALL_DIR = BASE_DIR / "data" / "raw" / "SisFall" / "SA01"
    OUTPUT_DIR = BASE_DIR / "data" / "research"
    
    # Tìm file Fall đầu tiên
    fall_files = list(SISFALL_DIR.glob("F*.txt"))
    adl_files = list(SISFALL_DIR.glob("D*.txt"))
    
    if fall_files:
        analyze_sisfall_file(fall_files[0], OUTPUT_DIR)
    
    if adl_files:
        analyze_sisfall_file(adl_files[0], OUTPUT_DIR)
