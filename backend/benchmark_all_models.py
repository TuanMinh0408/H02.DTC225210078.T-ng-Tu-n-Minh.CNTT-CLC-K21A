"""
Benchmark All Models — FallGuard AI
=====================================================
Script huấn luyện và đánh giá tất cả 5 mô hình trên cùng một
bộ dữ liệu SisFall, sau đó tạo báo cáo so sánh toàn diện.

Mô hình:
  1. Bi-LSTM + Attention
  2. Bi-GRU
  3. CNN-LSTM (1D-CNN + Bi-LSTM)
  4. Transformer Encoder
  5. TCN (Temporal Convolutional Network)

Output:
  - Checkpoint best model cho từng loại
  - Training curves, confusion matrix, ROC curve
  - Bảng so sánh tổng hợp (accuracy, precision, recall, F1, AUC)
  - File JSON kết quả chi tiết
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, random_split
import numpy as np
import json
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)

from model import get_model, count_parameters
from sisfall_loader import load_raw_windows_for_lstm


# ─── Cấu hình ────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = str(BASE_DIR / 'SisFall_dataset')
SAVE_DIR = BASE_DIR / 'data' / 'benchmark'
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Danh sách mô hình cần benchmark
MODEL_CONFIGS = {
    'lstm': {
        'display_name': 'Bi-LSTM + Attention',
        'params': {'input_size': 9, 'hidden_size': 128, 'num_layers': 2},
    },
    'gru': {
        'display_name': 'Bi-GRU',
        'params': {'input_size': 9, 'hidden_size': 128, 'num_layers': 2},
    },
    'cnn_lstm': {
        'display_name': 'CNN-LSTM',
        'params': {'input_size': 9},
    },
    'transformer': {
        'display_name': 'Transformer Encoder',
        'params': {'input_size': 9, 'd_model': 64, 'nhead': 4, 'num_layers': 2},
    },
    'tcn': {
        'display_name': 'TCN',
        'params': {'input_size': 9, 'num_channels': [32, 64, 64, 32], 'kernel_size': 3},
    },
}

# Hyperparameters chung
TRAINING_CONFIG = {
    'num_epochs': 50,
    'batch_size': 32,
    'learning_rate': 0.001,
    'patience': 10,
    'window_size': 200,
    'overlap': 100,
    'val_ratio': 0.15,
    'test_ratio': 0.15,
    'subjects': ['SA01', 'SA02', 'SA03', 'SA04', 'SA05',
                 'SA06', 'SA07', 'SA08', 'SA09', 'SA10'],
    'max_files': None,  # None = tải hết
}


class EarlyStopping:
    """Dừng sớm khi val loss không cải thiện."""
    def __init__(self, patience=10, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.should_stop = False

    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0


def prepare_shared_data():
    """
    Chuẩn bị 1 bộ dữ liệu duy nhất, chia train/val/test cố định
    để đảm bảo so sánh công bằng giữa các mô hình.
    """
    print("\n" + "=" * 60)
    print("  CHUẨN BỊ DỮ LIỆU CHUNG")
    print("=" * 60)

    cfg = TRAINING_CONFIG
    X, y = load_raw_windows_for_lstm(
        DATASET_DIR,
        subjects=cfg['subjects'],
        window_size=cfg['window_size'],
        overlap=cfg['overlap'],
        max_files=cfg['max_files']
    )
    print(f"  Tổng mẫu: {len(X)} | Falls: {np.sum(y==1)} | ADLs: {np.sum(y==0)}")

    # Z-score normalization
    mean = X.mean(axis=(0, 1), keepdims=True)
    std = X.std(axis=(0, 1), keepdims=True) + 1e-8
    X = (X - mean) / std
    np.save(SAVE_DIR / 'norm_mean.npy', mean.squeeze())
    np.save(SAVE_DIR / 'norm_std.npy', std.squeeze())

    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.LongTensor(y)
    dataset = TensorDataset(X_tensor, y_tensor)

    total = len(dataset)
    test_size = int(total * cfg['test_ratio'])
    val_size = int(total * cfg['val_ratio'])
    train_size = total - val_size - test_size

    # Seed cố định để mọi model dùng cùng split
    train_set, val_set, test_set = random_split(
        dataset, [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )

    # Class weights
    train_labels = y[train_set.indices]
    class_counts = np.bincount(train_labels, minlength=2)
    weights = len(train_labels) / (2 * class_counts + 1e-8)

    train_loader = DataLoader(train_set, batch_size=cfg['batch_size'], shuffle=True, drop_last=True)
    val_loader = DataLoader(val_set, batch_size=cfg['batch_size'], shuffle=False)
    test_loader = DataLoader(test_set, batch_size=cfg['batch_size'], shuffle=False)

    print(f"  Train: {len(train_set)} | Val: {len(val_set)} | Test: {len(test_set)}")
    print(f"  Class weights: ADL={weights[0]:.3f}, Fall={weights[1]:.3f}")

    return train_loader, val_loader, test_loader, weights


def train_single_model(model_type, model_config, train_loader, val_loader, class_weights, device):
    """Huấn luyện 1 mô hình và trả về history + best model."""
    cfg = TRAINING_CONFIG
    display_name = model_config['display_name']

    print(f"\n{'=' * 60}")
    print(f"  TRAINING: {display_name}")
    print(f"{'=' * 60}")

    model = get_model(model_type, **model_config['params']).to(device)
    num_params = count_parameters(model)
    print(f"  Parameters: {num_params:,}")

    optimizer = optim.Adam(model.parameters(), lr=cfg['learning_rate'], weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5)
    criterion = nn.CrossEntropyLoss(weight=torch.FloatTensor(class_weights).to(device))
    early_stopping = EarlyStopping(patience=cfg['patience'])

    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': [], 'lr': []}
    best_val_acc = 0
    best_state = None
    best_epoch = 0
    start_time = time.time()

    for epoch in range(1, cfg['num_epochs'] + 1):
        t0 = time.time()

        # ── Train ──
        model.train()
        total_loss, correct, total = 0, 0, 0
        for bx, by in train_loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item() * bx.size(0)
            correct += out.argmax(1).eq(by).sum().item()
            total += by.size(0)
        train_loss = total_loss / total
        train_acc = correct / total

        # ── Validate ──
        model.eval()
        total_loss, correct, total = 0, 0, 0
        with torch.no_grad():
            for bx, by in val_loader:
                bx, by = bx.to(device), by.to(device)
                out = model(bx)
                loss = criterion(out, by)
                total_loss += loss.item() * bx.size(0)
                correct += out.argmax(1).eq(by).sum().item()
                total += by.size(0)
        val_loss = total_loss / total
        val_acc = correct / total

        scheduler.step(val_loss)
        lr = optimizer.param_groups[0]['lr']

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        history['lr'].append(lr)

        elapsed = time.time() - t0
        print(f"  Epoch {epoch:3d}/{cfg['num_epochs']} | "
              f"TLoss: {train_loss:.4f} TAcc: {train_acc:.4f} | "
              f"VLoss: {val_loss:.4f} VAcc: {val_acc:.4f} | "
              f"LR: {lr:.6f} | {elapsed:.1f}s")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        early_stopping(val_loss)
        if early_stopping.should_stop:
            print(f"\n  ⚡ Early stopping at epoch {epoch}")
            break

    total_time = time.time() - start_time

    # Lưu best checkpoint
    ckpt_path = SAVE_DIR / f'best_{model_type}.pt'
    torch.save({
        'model_type': model_type,
        'model_state_dict': best_state,
        'epoch': best_epoch,
        'val_acc': best_val_acc,
        'input_size': model_config['params'].get('input_size', 9),
        'num_params': num_params,
        'training_time': total_time,
        'timestamp': datetime.now().isoformat(),
    }, ckpt_path)

    print(f"\n  ✅ {display_name} hoàn tất: {total_time:.1f}s | "
          f"Best epoch {best_epoch}, VAcc {best_val_acc:.4f}")
    print(f"  Saved: {ckpt_path}")

    return model, history, best_state, {
        'num_params': num_params,
        'training_time': total_time,
        'best_epoch': best_epoch,
        'best_val_acc': best_val_acc,
    }


@torch.no_grad()
def evaluate_model(model, test_loader, device):
    """Đánh giá mô hình trên tập test."""
    model.eval()
    all_preds, all_labels, all_probs = [], [], []

    for bx, by in test_loader:
        bx = bx.to(device)
        out = model(bx)
        probs = torch.softmax(out, dim=1)
        preds = out.argmax(1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(by.numpy())
        all_probs.extend(probs[:, 1].cpu().numpy())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)
    y_probs = np.array(all_probs)

    fpr, tpr, _ = roc_curve(y_true, y_probs)
    roc_auc = auc(fpr, tpr)

    metrics = {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
        'specificity': float(recall_score(y_true, y_pred, pos_label=0, zero_division=0)),
        'auc': float(roc_auc),
    }

    return metrics, y_true, y_pred, y_probs, fpr, tpr


# ─── Visualization ────────────────────────────────────────────────

def plot_training_curves_all(all_histories, save_dir):
    """Vẽ biểu đồ training curves cho tất cả mô hình trên cùng 1 figure."""
    colors = {
        'lstm': '#3b82f6',
        'gru': '#ef4444',
        'cnn_lstm': '#10b981',
        'transformer': '#f59e0b',
        'tcn': '#8b5cf6',
    }

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for model_type, history in all_histories.items():
        display = MODEL_CONFIGS[model_type]['display_name']
        color = colors.get(model_type, '#888888')
        epochs = range(1, len(history['train_loss']) + 1)

        # Loss
        axes[0].plot(epochs, history['val_loss'], '-', color=color,
                     label=display, linewidth=2, alpha=0.85)
        # Accuracy
        axes[1].plot(epochs, history['val_acc'], '-', color=color,
                     label=display, linewidth=2, alpha=0.85)

    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Validation Loss', fontsize=12)
    axes[0].set_title('Validation Loss Comparison', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Validation Accuracy', fontsize=12)
    axes[1].set_title('Validation Accuracy Comparison', fontsize=14, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    path = save_dir / 'training_curves_all.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_individual_training(model_type, history, save_dir):
    """Vẽ training curves riêng cho từng mô hình."""
    display = MODEL_CONFIGS[model_type]['display_name']
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    epochs = range(1, len(history['train_loss']) + 1)

    ax1.plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=2)
    ax1.plot(epochs, history['val_loss'], 'r-', label='Val Loss', linewidth=2)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title(f'Loss — {display}', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, history['train_acc'], 'b-', label='Train Acc', linewidth=2)
    ax2.plot(epochs, history['val_acc'], 'r-', label='Val Acc', linewidth=2)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title(f'Accuracy — {display}', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path = save_dir / f'training_{model_type}.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_confusion_matrices(all_cm_data, save_dir):
    """Vẽ confusion matrix cho tất cả mô hình."""
    n = len(all_cm_data)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4.5))
    if n == 1:
        axes = [axes]

    for i, (model_type, (y_true, y_pred)) in enumerate(all_cm_data.items()):
        display = MODEL_CONFIGS[model_type]['display_name']
        cm = confusion_matrix(y_true, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['ADL', 'Fall'],
                    yticklabels=['ADL', 'Fall'],
                    ax=axes[i], annot_kws={'size': 14})
        axes[i].set_xlabel('Predicted')
        axes[i].set_ylabel('True')
        axes[i].set_title(display, fontweight='bold', fontsize=11)

    plt.tight_layout()
    path = save_dir / 'confusion_matrices_all.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_roc_curves_all(all_roc_data, save_dir):
    """Vẽ ROC curve cho tất cả mô hình trên cùng 1 figure."""
    colors = {
        'lstm': '#3b82f6',
        'gru': '#ef4444',
        'cnn_lstm': '#10b981',
        'transformer': '#f59e0b',
        'tcn': '#8b5cf6',
    }

    fig, ax = plt.subplots(figsize=(8, 7))

    for model_type, (fpr, tpr, roc_auc) in all_roc_data.items():
        display = MODEL_CONFIGS[model_type]['display_name']
        color = colors.get(model_type, '#888888')
        ax.plot(fpr, tpr, color=color, lw=2.5,
                label=f'{display} (AUC = {roc_auc:.4f})', alpha=0.85)

    ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', alpha=0.5)
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC Curves — Model Comparison', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    path = save_dir / 'roc_curves_all.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_comparison_bar(all_metrics, all_meta, save_dir):
    """Vẽ biểu đồ cột so sánh metrics giữa các mô hình."""
    models = list(all_metrics.keys())
    metrics_keys = ['accuracy', 'precision', 'recall', 'f1_score', 'specificity', 'auc']
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Specificity', 'AUC']

    colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
    x = np.arange(len(metrics_keys))
    width = 0.15

    fig, ax = plt.subplots(figsize=(14, 7))
    for i, mt in enumerate(models):
        display = MODEL_CONFIGS[mt]['display_name']
        values = [all_metrics[mt].get(m, 0) for m in metrics_keys]
        bars = ax.bar(x + i * width, values, width, label=display,
                      color=colors[i % len(colors)], alpha=0.85)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.008,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Model Performance Comparison — FallGuard AI', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width * (len(models) - 1) / 2)
    ax.set_xticklabels(metric_labels, fontsize=11)
    ax.legend(fontsize=10, loc='upper left')
    ax.set_ylim(0, 1.15)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()

    path = save_dir / 'model_comparison_bar.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")

    # ── Bảng chi tiết (text) ──
    print("\n" + "=" * 90)
    print(f"  {'Model':<25} {'Params':>10} {'Time(s)':>8} {'Acc':>7} {'Prec':>7} {'Recall':>7} {'F1':>7} {'AUC':>7}")
    print("-" * 90)
    for mt in models:
        d = MODEL_CONFIGS[mt]['display_name']
        m = all_metrics[mt]
        meta = all_meta[mt]
        print(f"  {d:<25} {meta['num_params']:>10,} {meta['training_time']:>7.1f}s "
              f"{m['accuracy']:>7.4f} {m['precision']:>7.4f} {m['recall']:>7.4f} "
              f"{m['f1_score']:>7.4f} {m['auc']:>7.4f}")
    print("=" * 90)


def generate_summary_report(all_metrics, all_meta, save_dir):
    """Tạo file báo cáo tổng hợp."""
    report = {
        'title': 'FallGuard AI — Model Benchmark Report',
        'date': datetime.now().isoformat(),
        'dataset': {
            'name': 'SisFall',
            'subjects': TRAINING_CONFIG['subjects'],
            'window_size': TRAINING_CONFIG['window_size'],
            'overlap': TRAINING_CONFIG['overlap'],
        },
        'training_config': {
            'num_epochs': TRAINING_CONFIG['num_epochs'],
            'batch_size': TRAINING_CONFIG['batch_size'],
            'learning_rate': TRAINING_CONFIG['learning_rate'],
            'early_stopping_patience': TRAINING_CONFIG['patience'],
        },
        'results': {},
    }

    best_model = None
    best_f1 = 0

    for mt in all_metrics:
        display = MODEL_CONFIGS[mt]['display_name']
        report['results'][display] = {
            'model_type': mt,
            'architecture': display,
            'num_params': all_meta[mt]['num_params'],
            'training_time_seconds': round(all_meta[mt]['training_time'], 2),
            'best_epoch': all_meta[mt]['best_epoch'],
            'best_val_acc': round(all_meta[mt]['best_val_acc'], 4),
            'test_metrics': {k: round(v, 4) for k, v in all_metrics[mt].items()},
        }

        if all_metrics[mt]['f1_score'] > best_f1:
            best_f1 = all_metrics[mt]['f1_score']
            best_model = display

    report['best_model'] = best_model
    report['best_f1_score'] = round(best_f1, 4)

    path = save_dir / 'benchmark_report.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n  📄 Report saved: {path}")

    return report


# ─── MAIN ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  🏋️ FallGuard AI — Full Model Benchmark")
    print("  5 Models × SisFall Dataset")
    print("=" * 60)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"  Device: {device}")

    # 1. Chuẩn bị dữ liệu chung
    train_loader, val_loader, test_loader, class_weights = prepare_shared_data()

    # 2. Huấn luyện từng mô hình
    all_histories = {}
    all_models = {}
    all_meta = {}

    for model_type, config in MODEL_CONFIGS.items():
        model, history, best_state, meta = train_single_model(
            model_type, config, train_loader, val_loader, class_weights, device)

        # Load best state for evaluation
        model.load_state_dict(best_state)
        all_models[model_type] = model
        all_histories[model_type] = history
        all_meta[model_type] = meta

    # 3. Đánh giá trên tập test
    print("\n" + "=" * 60)
    print("  📊 ĐÁNH GIÁ TRÊN TẬP TEST")
    print("=" * 60)

    all_metrics = {}
    all_cm_data = {}
    all_roc_data = {}

    for model_type, model in all_models.items():
        display = MODEL_CONFIGS[model_type]['display_name']
        print(f"\n  Evaluating: {display}...")
        metrics, y_true, y_pred, y_probs, fpr, tpr = evaluate_model(model, test_loader, device)
        all_metrics[model_type] = metrics
        all_cm_data[model_type] = (y_true, y_pred)
        all_roc_data[model_type] = (fpr, tpr, metrics['auc'])

        print(f"    Acc: {metrics['accuracy']:.4f} | Prec: {metrics['precision']:.4f} | "
              f"Recall: {metrics['recall']:.4f} | F1: {metrics['f1_score']:.4f} | AUC: {metrics['auc']:.4f}")

    # 4. Vẽ biểu đồ
    print("\n  📈 Generating plots...")
    plot_training_curves_all(all_histories, SAVE_DIR)
    plot_confusion_matrices(all_cm_data, SAVE_DIR)
    plot_roc_curves_all(all_roc_data, SAVE_DIR)
    plot_comparison_bar(all_metrics, all_meta, SAVE_DIR)

    for mt, history in all_histories.items():
        plot_individual_training(mt, history, SAVE_DIR)

    # 5. Lưu history
    for mt, history in all_histories.items():
        with open(SAVE_DIR / f'history_{mt}.json', 'w') as f:
            json.dump(history, f, indent=2)

    # 6. Báo cáo
    report = generate_summary_report(all_metrics, all_meta, SAVE_DIR)

    print("\n" + "=" * 60)
    print(f"  🏆 BEST MODEL: {report['best_model']} (F1 = {report['best_f1_score']:.4f})")
    print("=" * 60)
    print(f"\n  📂 Tất cả kết quả lưu tại: {SAVE_DIR}")
    print("  ✅ Benchmark hoàn tất!")


if __name__ == '__main__':
    main()
