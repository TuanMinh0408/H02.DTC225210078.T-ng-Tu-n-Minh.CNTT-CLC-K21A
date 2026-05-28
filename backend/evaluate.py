"""
Evaluation Module — FallGuard AI
=====================================================
Đánh giá và so sánh mô hình với confusion matrix, ROC, metrics.
"""

import torch
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_curve, auc
)
from typing import Dict, Optional
from model import get_model


class ModelEvaluator:
    """Đánh giá mô hình trên tập test."""

    def __init__(self, save_dir=None):
        if save_dir is None:
            self.save_dir = Path(__file__).resolve().parent.parent / 'data' / 'evaluation'
        else:
            self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    @torch.no_grad()
    def predict(self, model, dataloader):
        """Chạy inference và trả về predictions, labels, probabilities."""
        model.eval()
        all_preds, all_labels, all_probs = [], [], []

        for bx, by in dataloader:
            bx = bx.to(self.device)
            out = model(bx)
            probs = torch.softmax(out, dim=1)
            preds = out.argmax(1)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(by.numpy())
            all_probs.extend(probs[:, 1].cpu().numpy())

        return np.array(all_preds), np.array(all_labels), np.array(all_probs)

    def compute_metrics(self, y_true, y_pred) -> Dict:
        """Tính các chỉ số đánh giá."""
        return {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
            'specificity': float(recall_score(y_true, y_pred, pos_label=0, zero_division=0)),
        }

    def plot_confusion_matrix(self, y_true, y_pred, model_name='Model'):
        """Vẽ confusion matrix."""
        cm = confusion_matrix(y_true, y_pred)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['ADL (Normal)', 'Fall'],
                    yticklabels=['ADL (Normal)', 'Fall'], ax=ax,
                    annot_kws={'size': 16})
        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_title(f'Confusion Matrix — {model_name}', fontsize=14, fontweight='bold')
        plt.tight_layout()

        path = self.save_dir / f'confusion_matrix_{model_name.lower().replace(" ", "_")}.png'
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  Saved: {path}")
        return str(path)

    def plot_roc_curve(self, y_true, y_probs, model_name='Model'):
        """Vẽ ROC curve."""
        fpr, tpr, _ = roc_curve(y_true, y_probs)
        roc_auc = auc(fpr, tpr)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(fpr, tpr, color='#3b82f6', lw=2, label=f'{model_name} (AUC = {roc_auc:.4f})')
        ax.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', alpha=0.5)
        ax.set_xlabel('False Positive Rate', fontsize=12)
        ax.set_ylabel('True Positive Rate', fontsize=12)
        ax.set_title(f'ROC Curve — {model_name}', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', fontsize=11)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        path = self.save_dir / f'roc_{model_name.lower().replace(" ", "_")}.png'
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  Saved: {path}")
        return str(path), roc_auc

    def plot_training_curves(self, history, model_name='Model'):
        """Vẽ biểu đồ loss và accuracy trong quá trình training."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        epochs = range(1, len(history['train_loss']) + 1)

        # Loss
        ax1.plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=2)
        ax1.plot(epochs, history['val_loss'], 'r-', label='Val Loss', linewidth=2)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.set_title(f'Training & Validation Loss — {model_name}', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Accuracy
        ax2.plot(epochs, history['train_acc'], 'b-', label='Train Acc', linewidth=2)
        ax2.plot(epochs, history['val_acc'], 'r-', label='Val Acc', linewidth=2)
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.set_title(f'Training & Validation Accuracy — {model_name}', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        path = self.save_dir / f'training_curves_{model_name.lower().replace(" ", "_")}.png'
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  Saved: {path}")
        return str(path)

    def plot_comparison(self, results: Dict[str, Dict]):
        """Vẽ biểu đồ so sánh giữa các mô hình."""
        models = list(results.keys())
        metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'specificity']
        metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Specificity']

        x = np.arange(len(metrics))
        width = 0.15
        colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

        fig, ax = plt.subplots(figsize=(12, 6))
        for i, model_name in enumerate(models):
            values = [results[model_name].get(m, 0) for m in metrics]
            bars = ax.bar(x + i * width, values, width, label=model_name, color=colors[i % len(colors)])
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f'{val:.3f}', ha='center', va='bottom', fontsize=9)

        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Model Comparison — FallGuard AI', fontsize=14, fontweight='bold')
        ax.set_xticks(x + width * (len(models) - 1) / 2)
        ax.set_xticklabels(metric_labels)
        ax.legend()
        ax.set_ylim(0, 1.15)
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        path = self.save_dir / 'model_comparison.png'
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"  Saved: {path}")
        return str(path)

    def evaluate_model(self, model, dataloader, model_name='Model'):
        """Đánh giá toàn diện 1 mô hình."""
        model = model.to(self.device)
        preds, labels, probs = self.predict(model, dataloader)

        metrics = self.compute_metrics(labels, preds)
        self.plot_confusion_matrix(labels, preds, model_name)
        _, roc_auc = self.plot_roc_curve(labels, probs, model_name)
        metrics['auc'] = float(roc_auc)

        print(f"\n  === {model_name} ===")
        for k, v in metrics.items():
            print(f"  {k}: {v:.4f}")

        report = classification_report(labels, preds, target_names=['ADL', 'Fall'])
        print(f"\n{report}")

        # Save metrics
        path = self.save_dir / f'metrics_{model_name.lower().replace(" ", "_")}.json'
        with open(path, 'w') as f:
            json.dump(metrics, f, indent=2)

        return metrics

    def full_comparison(self, test_loader, model_dir, model_types=None):
        """So sánh nhiều mô hình trên cùng tập test."""
        if model_types is None:
            model_types = ['lstm', 'gru', 'cnn_lstm', 'transformer', 'tcn']

        model_dir = Path(model_dir)
        results = {}

        for mt in model_types:
            # Try model-specific checkpoint first, then generic
            ckpt_path = model_dir / f'best_{mt}.pt'
            if not ckpt_path.exists():
                ckpt_path = model_dir / 'best_model.pt'
            if not ckpt_path.exists():
                print(f"  Skip {mt}: no checkpoint found")
                continue

            ckpt = torch.load(ckpt_path, map_location=self.device)
            model = get_model(mt, input_size=ckpt.get('input_size', 9))
            model.load_state_dict(ckpt['model_state_dict'])

            metrics = self.evaluate_model(model, test_loader, mt.upper())
            results[mt.upper()] = metrics

        if len(results) > 1:
            self.plot_comparison(results)

        # Save all results
        with open(self.save_dir / 'comparison_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        return results


if __name__ == '__main__':
    print("Evaluation module loaded. Use ModelEvaluator class to evaluate trained models.")
