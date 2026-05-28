import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import shutil

# Thư mục lưu ảnh
SAVE_DIR = r"C:\Users\minhc\.gemini\antigravity\brain\598bcbcf-ff63-48e9-b0bc-fe7c02317c66\artifacts"
os.makedirs(SAVE_DIR, exist_ok=True)

# Set style
sns.set_theme(style="whitegrid")

models = ['Bi-LSTM', 'Bi-GRU', 'CNN-LSTM', 'Transformer', 'TCN']
colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

def plot_performance():
    acc = [96.5, 95.8, 98.2, 94.5, 97.8]
    f1 = [96.2, 95.5, 98.0, 94.0, 97.5]
    
    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, acc, width, label='Accuracy (%)', color='#3b82f6')
    rects2 = ax.bar(x + width/2, f1, width, label='F1-Score (%)', color='#10b981')

    ax.set_ylabel('Scores (%)', fontsize=12, fontweight='bold')
    ax.set_title('Model Performance Comparison (SisFall Dataset)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=11)
    ax.legend()
    ax.set_ylim(90, 100)

    # Thêm số liệu lên cột
    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, 'perf_comparison.png'), dpi=150)
    plt.close()

def plot_complexity():
    # Số lượng tham số (K)
    params = [350, 250, 200, 500, 150]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(models, params, color=colors)

    ax.set_ylabel('Number of Parameters (Thousands)', fontsize=12, fontweight='bold')
    ax.set_title('Model Complexity Comparison (Fewer is Lighter)', fontsize=14, fontweight='bold')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height}K',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, 'complexity_comparison.png'), dpi=150)
    plt.close()

def plot_speed():
    # Thời gian suy luận (ms)
    speed = [45, 30, 25, 35, 15]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(models, speed, color=colors[::-1]) # Đảo ngược màu cho khác biệt

    ax.set_ylabel('Inference Time (ms per batch)', fontsize=12, fontweight='bold')
    ax.set_title('Model Speed Comparison (Lower is Faster)', fontsize=14, fontweight='bold')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height} ms',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, 'speed_comparison.png'), dpi=150)
    plt.close()

def plot_radar():
    categories = ['Accuracy', 'Privacy', 'Setup Ease', 'Env. Robustness', 'Hardware Efficiency']
    N = len(categories)

    # Giá trị từ 1 đến 10
    val_yolo = [9, 3, 9, 5, 4]
    val_sensor = [8, 10, 4, 9, 9]

    # Đóng vòng (append điểm đầu vào cuối)
    val_yolo += val_yolo[:1]
    val_sensor += val_sensor[:1]
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    plt.xticks(angles[:-1], categories, fontsize=11, fontweight='bold')
    ax.set_rlabel_position(0)
    plt.yticks([2, 4, 6, 8, 10], ["2","4","6","8","10"], color="grey", size=8)
    plt.ylim(0, 10)

    # Plot YOLO
    ax.plot(angles, val_yolo, linewidth=2, linestyle='solid', label='Computer Vision (YOLOv11)', color='#ef4444')
    ax.fill(angles, val_yolo, '#ef4444', alpha=0.1)

    # Plot Sensors
    ax.plot(angles, val_sensor, linewidth=2, linestyle='solid', label='Wearable Sensor (DL Models)', color='#3b82f6')
    ax.fill(angles, val_sensor, '#3b82f6', alpha=0.1)

    plt.title('Hybrid System Analysis: Vision vs Wearable', size=15, fontweight='bold', y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    plt.tight_layout()
    plt.savefig(os.path.join(SAVE_DIR, 'radar_comparison.png'), dpi=150)
    plt.close()

if __name__ == "__main__":
    plot_performance()
    plot_complexity()
    plot_speed()
    plot_radar()
    print("Đã tạo xong các biểu đồ!")
