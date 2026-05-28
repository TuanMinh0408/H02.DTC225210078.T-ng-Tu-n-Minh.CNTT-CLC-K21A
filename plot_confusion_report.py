"""
Create publication-quality confusion matrix subplots and save as PNG/PDF.

Usage:
    python plot_confusion_report.py --input matrices.json --out confusion_report.png --dpi 300

Input JSON format example:
{
  "models": [
    {"name": "Bi-LSTM + Attention", "labels": ["ADL","Fall"], "matrix": [[4058,303],[254,2998]]},
    {"name": "Bi-GRU", "labels": ["ADL","Fall"], "matrix": [[4134,227],[273,2979]]}
  ]
}

If no input provided, the script will render a small built-in example (the example from the dashboard).
"""

import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
import os


def draw_confusion_matrices(models, out_path, dpi=300, cmap='Blues', cols=None, figsize=(18,6)):
    """Draw multiple confusion matrices in a grid.

    - `cols`: number of columns (default: min(3, n_models)).
    """
    n = len(models)
    if n == 0:
        raise ValueError('No models to plot')

    if cols is None:
        cols = min(3, n)
    cols = int(cols)
    rows = int(np.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=figsize, constrained_layout=True)
    axes = np.array(axes).reshape(-1)

    vmax = max(np.max(np.array(m['matrix'])) for m in models)

    for idx, m in enumerate(models):
        ax = axes[idx]
        mat = np.array(m['matrix'])
        labels = m.get('labels', ["ADL", "Fall"])
        im = ax.imshow(mat, interpolation='nearest', cmap=cmap, vmin=0, vmax=vmax)
        ax.set_title(m.get('name', ''), fontsize=12, fontweight='600')
        ax.set_xticks(np.arange(len(labels)))
        ax.set_yticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_yticklabels(labels, fontsize=10)
        ax.set_xlabel('Predicted', fontsize=10)
        ax.set_ylabel('True', fontsize=10)

        # Annotations
        thresh = mat.max() / 2.0 if mat.size else 0
        for i in range(mat.shape[0]):
            for j in range(mat.shape[1]):
                c = mat[i, j]
                color = 'white' if c > thresh else 'black'
                ax.text(j, i, f"{int(c):,}", ha="center", va="center", color=color, fontsize=11, fontweight='700')

        # compact colorbar per row: attach to rightmost subplot in the row
        if (idx % cols) == (cols - 1) or idx == n - 1:
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # Turn off unused axes
    for ax in axes[n:]:
        ax.axis('off')

    # Save output
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    fig.suptitle('Confusion Matrices', fontsize=16, fontweight='700')
    fig.savefig(out_path, dpi=dpi)
    print(f"Saved figure to {out_path}")


def compute_binary_metrics(mat):
    """Assume 2x2 matrix with order [ADL, Fall] for rows/cols. Return precision, recall, f1 for Fall."""
    mat = np.array(mat)
    if mat.shape != (2, 2):
        return {'precision': None, 'recall': None, 'f1': None}
    tn, fp = mat[0, 0], mat[0, 1]
    fn, tp = mat[1, 0], mat[1, 1]
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return {'precision': precision, 'recall': recall, 'f1': f1}


def draw_summary_bar(models, out_path, dpi=300, figsize=(10,6)):
    """Draw precision/recall/f1 bar chart for the 'Fall' class across models."""
    names = [m.get('name','') for m in models]
    metrics = [compute_binary_metrics(m['matrix']) for m in models]
    precisions = [m['precision'] for m in metrics]
    recalls = [m['recall'] for m in metrics]
    f1s = [m['f1'] for m in metrics]

    x = np.arange(len(names))
    width = 0.25

    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(x - width, precisions, width, label='Precision', color='#4f81bd')
    ax.bar(x, recalls, width, label='Recall', color='#c0504d')
    ax.bar(x + width, f1s, width, label='F1', color='#9bbb59')

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=25, ha='right')
    ax.set_ylim(0, 1.0)
    ax.set_ylabel('Score')
    ax.set_title('Fall-class Precision / Recall / F1 by Model')
    ax.legend()

    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    print(f"Saved summary figure to {out_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot confusion matrices for report')
    parser.add_argument('--input', '-i', help='Input JSON file with matrices', default=None)
    parser.add_argument('--out', '-o', help='Output image path (png/pdf)', default='confusion_report.png')
    parser.add_argument('--dpi', type=int, default=300, help='Output DPI')
    parser.add_argument('--cols', type=int, default=None, help='Number of columns for grid layout (default: up to 3)')
    parser.add_argument('--summary', action='store_true', help='Also render a summary Precision/Recall/F1 bar chart (saved as <out>_summary.png)')
    args = parser.parse_args()

    if args.input and os.path.exists(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        models = data.get('models', [])
    else:
        # fallback example (from provided attachment)
        models = [
            {"name": "Bi-LSTM + Attention", "labels": ["ADL","Fall"], "matrix": [[4058,303],[254,2998]]},
            {"name": "Bi-GRU", "labels": ["ADL","Fall"], "matrix": [[4134,227],[273,2979]]},
            {"name": "CNN-LSTM", "labels": ["ADL","Fall"], "matrix": [[4067,294],[245,3007]]},
            {"name": "Transformer Encoder", "labels": ["ADL","Fall"], "matrix": [[3934,427],[362,2890]]},
            {"name": "TCN", "labels": ["ADL","Fall"], "matrix": [[3927,434],[257,2995]]},
        ]

    # Draw grid (auto columns unless specified)
    draw_confusion_matrices(models, args.out, dpi=args.dpi, cols=args.cols)

    # Optionally draw summary bar chart
    if args.summary:
        base, ext = os.path.splitext(args.out)
        summary_out = f"{base}_summary.png"
        draw_summary_bar(models, summary_out, dpi=args.dpi)
