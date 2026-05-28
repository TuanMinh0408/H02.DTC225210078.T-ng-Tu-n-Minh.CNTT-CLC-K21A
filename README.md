# 🛡️ FallGuard AI — Hệ Thống Phát Hiện Té Ngã Thông Minh

> **Đồ án tốt nghiệp ngành Công nghệ Thông tin**
> Ứng dụng Học sâu trong nhận dạng hành vi té ngã của người cao tuổi

**Sinh viên:** Tăng Tuấn Minh (DTC225210078) — CNTT K21 CLC
**GVHD:** TS. Nguyễn Tuấn Anh — Khoa CNTT, ĐH CNTT&TT Thái Nguyên

---

## 📋 Tổng Quan

FallGuard AI là hệ thống giám sát thông minh sử dụng **Deep Learning** để phát hiện hành vi té ngã của người cao tuổi qua camera giám sát trong thời gian thực. Hệ thống kết hợp:

- **YOLOv11-Pose**: Ước lượng tư thế 17 điểm khung xương
- **Bi-LSTM + Attention**: Phân loại chuỗi chuyển động
- **Heuristic Rules**: Phân tích vận tốc, tỷ lệ khung hình, vị trí đầu

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────┐     WebSocket      ┌──────────────────────┐
│   Browser/App   │ ◄────────────────► │   FastAPI Backend    │
│   Dashboard     │                    │                      │
│   (HTML/CSS/JS) │                    │  ┌────────────────┐  │
└─────────────────┘                    │  │ YOLOv11-Pose   │  │
                                       │  │ (17 keypoints) │  │
                                       │  └───────┬────────┘  │
                                       │          ▼           │
                                       │  ┌────────────────┐  │
                                       │  │ Fall Detector   │  │
                                       │  │ (Heuristic)    │  │
                                       │  └───────┬────────┘  │
                                       │          ▼           │
                                       │  ┌────────────────┐  │
                                       │  │ SQLite DB      │  │
                                       │  │ (History)      │  │
                                       │  └────────────────┘  │
                                       └──────────────────────┘
```

## ⚡ Tính Năng

| Tính năng | Mô tả |
|-----------|-------|
| 🎥 Real-time Detection | Phát hiện té ngã từ webcam với FPS > 15 |
| 📊 Statistics Dashboard | Biểu đồ thống kê theo ngày/tuần/giờ |
| 📜 History Log | Lưu trữ và xem lại lịch sử sự cố |
| ⚙️ Settings Panel | Tùy chỉnh ngưỡng detection, notifications |
| 🔔 Browser Notification | Cảnh báo qua browser + âm thanh |
| 📥 CSV Export | Xuất dữ liệu lịch sử ra CSV |
| 🧠 Multi-model Training | LSTM, GRU, CNN-LSTM, Transformer, TCN trên SisFall dataset |
| 📈 Model Evaluation | Confusion matrix, ROC curve, F1-score, benchmark so sánh 5 mô hình |

## 🚀 Cài Đặt & Chạy

### Yêu cầu
- Python 3.10+
- Webcam

### Bước 1: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy server
```bash
cd backend
python main.py
```

### Bước 3: Truy cập Dashboard
Mở trình duyệt tại: **http://localhost:8000**

## 📂 Cấu Trúc Dự Án

```
graduation_project/
├── backend/
│   ├── main.py              # FastAPI server + WebSocket
│   ├── detector.py           # YOLOv11 fall detection engine
│   ├── model.py              # LSTM/GRU/CNN-LSTM/Transformer/TCN architectures
│   ├── train_logic.py        # Training pipeline
│   ├── evaluate.py           # Metrics & evaluation
│   ├── benchmark_all_models.py # Benchmark so sánh 5 mô hình
│   ├── sisfall_loader.py     # SisFall dataset loader
│   ├── data_pipeline.py      # Video keypoint extraction
│   ├── fusion_dataset.py     # Multimodal fusion dataset
│   └── research_sisfall.py   # SisFall data analysis
├── frontend/
│   ├── index.html            # Dashboard UI
│   ├── style.css             # Premium dark theme
│   └── script.js             # Client logic + charts
├── SisFall_dataset/          # SisFall sensor data (38 subjects)
├── data/
│   ├── captures/             # Fall capture images
│   ├── models/               # Trained model checkpoints
│   ├── evaluation/           # Evaluation plots
│   └── fall_detection.db     # SQLite database
├── docs/
│   ├── architecture.md       # System architecture
│   └── requirements.md       # SRS document
├── requirements.txt
├── yolo11n-pose.pt           # YOLOv11 Pose model weights
└── README.md
```

## 🧠 Huấn Luyện Model

```bash
cd backend
# Huấn luyện LSTM với SisFall dataset
python train_logic.py

# Benchmark so sánh tất cả 5 mô hình
python benchmark_all_models.py

# Đánh giá model
python evaluate.py
```

## 📊 Dataset

Sử dụng bộ dữ liệu **SisFall** (Sucerquia et al., 2017):
- 38 subjects (23 adults + 15 elderly)
- 19 ADL activities + 15 fall types
- 4,510 recordings
- 3 sensors (ADXL345, ITG3200, MMA8451Q) @ 200Hz

## 📄 License

Dự án phục vụ mục đích học thuật — Đồ án tốt nghiệp.
