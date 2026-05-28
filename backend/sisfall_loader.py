"""
SisFall Dataset Loader — FallGuard AI
=====================================================
Module chuyên dụng để đọc, tiền xử lý và chuẩn bị dữ liệu
từ bộ SisFall cho quá trình huấn luyện mô hình Deep Learning.

SisFall gồm 4510 bản ghi từ 38 subjects (23 adults + 15 elderly),
mỗi file chứa 9 cột (3 sensors × 3 axes) lấy mẫu ở 200Hz.

Reference:
    Sucerquia, A., López, J.D., & Vargas-Bonilla, J.F. (2017).
    SisFall: A Fall and Movement Dataset. Sensors, 17(1), 198.
"""

import numpy as np
import os
from pathlib import Path
from typing import Tuple, List, Optional, Dict
import warnings

# ─── Hằng số cấu hình ───────────────────────────────────────────
SAMPLING_RATE = 200  # Hz
NUM_SENSOR_COLUMNS = 9

# Hệ số chuyển đổi từ bits sang đơn vị vật lý
ADXL345_SCALE = (2 * 16) / (2 ** 13)    # ±16g, 13-bit → g
ITG3200_SCALE = (2 * 2000) / (2 ** 16)  # ±2000°/s, 16-bit → °/s
MMA8451Q_SCALE = (2 * 8) / (2 ** 14)    # ±8g, 14-bit → g

# Ánh xạ mã hoạt động
FALL_CODES = [f'F{i:02d}' for i in range(1, 16)]  # F01–F15
ADL_CODES = [f'D{i:02d}' for i in range(1, 20)]   # D01–D19


def parse_sisfall_file(file_path: str) -> Optional[np.ndarray]:
    """
    Đọc một file dữ liệu SisFall và trả về ma trận numpy.

    Args:
        file_path: Đường dẫn tới file .txt

    Returns:
        np.ndarray shape (N, 9) hoặc None nếu lỗi.
        Cột 0-2: ADXL345 Acc (X, Y, Z) [bits]
        Cột 3-5: ITG3200 Gyro (X, Y, Z) [bits]
        Cột 6-8: MMA8451Q Acc (X, Y, Z) [bits]
    """
    try:
        rows = []
        with open(file_path, 'r') as f:
            for line in f:
                clean = line.strip().rstrip(';').strip()
                if not clean:
                    continue
                vals = [int(v.strip()) for v in clean.split(',') if v.strip()]
                if len(vals) == NUM_SENSOR_COLUMNS:
                    rows.append(vals)

        if not rows:
            return None
        return np.array(rows, dtype=np.float64)

    except Exception as e:
        warnings.warn(f"Lỗi đọc file {file_path}: {e}")
        return None


def convert_to_physical_units(raw_data: np.ndarray) -> np.ndarray:
    """
    Chuyển đổi dữ liệu thô (bits) sang đơn vị vật lý (g, °/s).

    Args:
        raw_data: np.ndarray shape (N, 9) ở đơn vị bits

    Returns:
        np.ndarray shape (N, 9):
          - Cột 0-2: ADXL345 [g]
          - Cột 3-5: ITG3200 [°/s]
          - Cột 6-8: MMA8451Q [g]
    """
    converted = raw_data.copy()
    converted[:, 0:3] *= ADXL345_SCALE
    converted[:, 3:6] *= ITG3200_SCALE
    converted[:, 6:9] *= MMA8451Q_SCALE
    return converted


def compute_features(data: np.ndarray, window_size: int = 200, overlap: int = 100) -> np.ndarray:
    """
    Trích xuất đặc trưng thống kê từ cửa sổ trượt (sliding window).

    Với mỗi cửa sổ, tính toán 12 đặc trưng cho mỗi trong 9 kênh:
      mean, std, min, max, rms, peak_to_peak, zero_crossing_rate,
      energy, skewness, kurtosis, percentile_25, percentile_75

    Args:
        data: np.ndarray shape (N, 9) đã convert sang vật lý
        window_size: Kích thước cửa sổ (samples). 200 = 1 giây ở 200Hz
        overlap: Số samples chồng lấn

    Returns:
        np.ndarray shape (num_windows, 9 * 12) = (num_windows, 108)
    """
    from scipy import stats as sp_stats

    step = window_size - overlap
    num_windows = max(0, (len(data) - window_size) // step + 1)

    if num_windows == 0:
        return np.array([]).reshape(0, 108)

    all_features = []

    for i in range(num_windows):
        start = i * step
        end = start + window_size
        window = data[start:end]

        window_feats = []
        for ch in range(9):
            channel = window[:, ch]
            mean_val = np.mean(channel)
            std_val = np.std(channel)
            min_val = np.min(channel)
            max_val = np.max(channel)
            rms_val = np.sqrt(np.mean(channel ** 2))
            p2p_val = max_val - min_val

            # Zero-crossing rate
            zero_crossings = np.sum(np.diff(np.sign(channel - mean_val)) != 0)
            zcr = zero_crossings / len(channel)

            # Energy
            energy = np.sum(channel ** 2) / len(channel)

            # Skewness & Kurtosis
            skew_val = sp_stats.skew(channel)
            kurt_val = sp_stats.kurtosis(channel)

            # Percentiles
            p25 = np.percentile(channel, 25)
            p75 = np.percentile(channel, 75)

            window_feats.extend([
                mean_val, std_val, min_val, max_val, rms_val, p2p_val,
                zcr, energy, skew_val, kurt_val, p25, p75
            ])

        all_features.append(window_feats)

    return np.array(all_features)


def compute_svm(data: np.ndarray) -> np.ndarray:
    """
    Tính Signal Vector Magnitude (SVM) cho cả 3 sensor.

    SVM = sqrt(x² + y² + z²)

    Returns:
        np.ndarray shape (N, 3) — SVM cho ADXL345, ITG3200, MMA8451Q
    """
    svm_adxl = np.sqrt(np.sum(data[:, 0:3] ** 2, axis=1))
    svm_itg = np.sqrt(np.sum(data[:, 3:6] ** 2, axis=1))
    svm_mma = np.sqrt(np.sum(data[:, 6:9] ** 2, axis=1))
    return np.column_stack([svm_adxl, svm_itg, svm_mma])


def extract_filename_info(filename: str) -> Dict[str, str]:
    """
    Phân tích tên file SisFall để lấy thông tin.

    Ví dụ: F05_SA01_R04.txt → {'activity': 'F05', 'subject': 'SA01', 'trial': 'R04', 'is_fall': True}
    """
    stem = Path(filename).stem
    parts = stem.split('_')
    if len(parts) != 3:
        return {'activity': '', 'subject': '', 'trial': '', 'is_fall': False}

    activity_code = parts[0]
    return {
        'activity': activity_code,
        'subject': parts[1],
        'trial': parts[2],
        'is_fall': activity_code.startswith('F')
    }


def load_dataset(
    dataset_dir: str,
    subjects: Optional[List[str]] = None,
    use_physical_units: bool = True,
    window_size: int = 200,
    overlap: int = 100,
    use_features: bool = True,
    max_files: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    """
    Tải toàn bộ hoặc một phần bộ dữ liệu SisFall.

    Args:
        dataset_dir: Thư mục gốc chứa các thư mục SA01, SA02, ... SE15
        subjects: Danh sách subjects cần tải (vd: ['SA01', 'SA02']).
                  Nếu None, tải tất cả.
        use_physical_units: Chuyển đổi sang đơn vị vật lý?
        window_size: Kích thước cửa sổ trượt (samples)
        overlap: Chồng lấn giữa các cửa sổ
        use_features: Nếu True, trích xuất features. Nếu False, trả về raw windows
        max_files: Giới hạn số file tối đa (cho debug/test nhanh)

    Returns:
        X: np.ndarray — Dữ liệu đặc trưng
        y: np.ndarray — Nhãn (0 = ADL, 1 = Fall)
        metadata: List[Dict] — Thông tin chi tiết mỗi mẫu
    """
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục dataset: {dataset_dir}")

    # Xác định danh sách subjects
    if subjects is None:
        subject_dirs = sorted([
            d for d in dataset_path.iterdir()
            if d.is_dir() and (d.name.startswith('SA') or d.name.startswith('SE'))
        ])
    else:
        subject_dirs = [dataset_path / s for s in subjects if (dataset_path / s).exists()]

    all_X = []
    all_y = []
    all_meta = []
    file_count = 0

    for subject_dir in subject_dirs:
        txt_files = sorted(subject_dir.glob('*.txt'))

        for txt_file in txt_files:
            if max_files is not None and file_count >= max_files:
                break

            # Lấy metadata từ filename
            info = extract_filename_info(txt_file.name)
            if not info['activity']:
                continue

            # Đọc dữ liệu
            raw = parse_sisfall_file(str(txt_file))
            if raw is None or len(raw) < window_size:
                continue

            # Chuyển đổi đơn vị
            data = convert_to_physical_units(raw) if use_physical_units else raw

            # Trích xuất features hoặc windows
            if use_features:
                features = compute_features(data, window_size, overlap)
            else:
                # Trả về raw sliding windows cho LSTM
                step = window_size - overlap
                num_windows = (len(data) - window_size) // step + 1
                features = np.array([
                    data[i * step: i * step + window_size]
                    for i in range(num_windows)
                ])

            if len(features) == 0:
                continue

            # Gán nhãn
            label = 1 if info['is_fall'] else 0
            labels = np.full(len(features), label)

            all_X.append(features)
            all_y.append(labels)

            for _ in range(len(features)):
                all_meta.append(info)

            file_count += 1

        if max_files is not None and file_count >= max_files:
            break

    if not all_X:
        return np.array([]), np.array([]), []

    X = np.concatenate(all_X, axis=0)
    y = np.concatenate(all_y, axis=0)

    return X, y, all_meta


def load_raw_windows_for_lstm(
    dataset_dir: str,
    subjects: Optional[List[str]] = None,
    window_size: int = 200,
    overlap: int = 100,
    max_files: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Tải dữ liệu dạng cửa sổ trượt cho mô hình LSTM/GRU.

    Returns:
        X: np.ndarray shape (num_samples, window_size, 9)
        y: np.ndarray shape (num_samples,) — 0=ADL, 1=Fall
    """
    X, y, _ = load_dataset(
        dataset_dir, subjects=subjects,
        use_physical_units=True,
        window_size=window_size,
        overlap=overlap,
        use_features=False,
        max_files=max_files
    )
    return X, y


def get_dataset_summary(dataset_dir: str) -> Dict:
    """
    Thống kê tổng quan về bộ dữ liệu.
    """
    dataset_path = Path(dataset_dir)
    summary = {
        'total_subjects': 0,
        'adult_subjects': 0,
        'elderly_subjects': 0,
        'total_files': 0,
        'fall_files': 0,
        'adl_files': 0,
        'subjects': []
    }

    for d in sorted(dataset_path.iterdir()):
        if not d.is_dir():
            continue
        if d.name.startswith('SA'):
            summary['adult_subjects'] += 1
            summary['total_subjects'] += 1
        elif d.name.startswith('SE'):
            summary['elderly_subjects'] += 1
            summary['total_subjects'] += 1
        else:
            continue

        files = list(d.glob('*.txt'))
        fall_count = sum(1 for f in files if f.name.startswith('F'))
        adl_count = sum(1 for f in files if f.name.startswith('D'))

        summary['total_files'] += len(files)
        summary['fall_files'] += fall_count
        summary['adl_files'] += adl_count
        summary['subjects'].append({
            'id': d.name,
            'type': 'Adult' if d.name.startswith('SA') else 'Elderly',
            'total_files': len(files),
            'falls': fall_count,
            'adls': adl_count
        })

    return summary


# ─── Main: Test thử ──────────────────────────────────────────────
if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATASET_DIR = BASE_DIR / 'SisFall_dataset'

    print("=" * 60)
    print("  SisFall Dataset Loader — FallGuard AI")
    print("=" * 60)

    # 1. Thống kê dataset
    summary = get_dataset_summary(str(DATASET_DIR))
    print(f"\n📊 Tổng quan Dataset:")
    print(f"   Tổng subjects: {summary['total_subjects']} ({summary['adult_subjects']} adults, {summary['elderly_subjects']} elderly)")
    print(f"   Tổng files: {summary['total_files']} ({summary['fall_files']} falls, {summary['adl_files']} ADLs)")

    # 2. Test đọc 1 file
    print(f"\n📂 Test đọc SA01/F01_SA01_R01.txt:")
    test_file = DATASET_DIR / 'SA01' / 'F01_SA01_R01.txt'
    if test_file.exists():
        raw = parse_sisfall_file(str(test_file))
        if raw is not None:
            print(f"   Raw shape: {raw.shape}")
            converted = convert_to_physical_units(raw)
            print(f"   Converted shape: {converted.shape}")
            svm = compute_svm(converted)
            print(f"   SVM shape: {svm.shape}")
            features = compute_features(converted)
            print(f"   Features shape: {features.shape} (108 features per window)")

    # 3. Test load mini dataset (3 subjects)
    print(f"\n🔄 Test load dataset (3 subjects, feature mode):")
    X, y, meta = load_dataset(str(DATASET_DIR), subjects=['SA01', 'SA02', 'SA03'], max_files=20)
    if len(X) > 0:
        print(f"   X shape: {X.shape}")
        print(f"   y shape: {y.shape}")
        print(f"   Falls: {np.sum(y == 1)}, ADLs: {np.sum(y == 0)}")

    # 4. Test load raw windows cho LSTM
    print(f"\n🧠 Test load raw windows cho LSTM (2 subjects):")
    X_lstm, y_lstm = load_raw_windows_for_lstm(str(DATASET_DIR), subjects=['SA01'], max_files=10)
    if len(X_lstm) > 0:
        print(f"   X shape: {X_lstm.shape} (samples, timesteps, channels)")
        print(f"   y shape: {y_lstm.shape}")
        print(f"   Falls: {np.sum(y_lstm == 1)}, ADLs: {np.sum(y_lstm == 0)}")

    print("\n✅ SisFall Loader test hoàn tất!")
