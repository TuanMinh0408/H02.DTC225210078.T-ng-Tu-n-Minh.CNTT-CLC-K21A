"""
Training Pipeline — FallGuard AI
=====================================================
Pipeline huấn luyện hoàn chỉnh cho mô hình phân loại té ngã.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, random_split
import numpy as np
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

from model import get_model, count_parameters
from sisfall_loader import load_raw_windows_for_lstm


class EarlyStopping:
    """Dừng sớm khi val loss không cải thiện sau patience epochs."""
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


class TrainingPipeline:
    """Pipeline huấn luyện end-to-end cho FallGuard AI."""

    def __init__(self, model_type='lstm', input_size=9, hidden_size=128,
                 num_layers=2, learning_rate=0.001, batch_size=32,
                 num_epochs=50, patience=10, device=None, save_dir=None):
        self.model_type = model_type
        self.input_size = input_size
        self.batch_size = batch_size
        self.num_epochs = num_epochs

        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        if save_dir is None:
            self.save_dir = Path(__file__).resolve().parent.parent / 'data' / 'models'
        else:
            self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.model = get_model(model_type, input_size=input_size,
                               hidden_size=hidden_size, num_layers=num_layers).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate, weight_decay=1e-4)
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5, verbose=True)
        self.early_stopping = EarlyStopping(patience=patience)
        self.criterion = None
        self.test_loader = None
        self.history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': [], 'lr': []}

        print(f"Model: {model_type.upper()} | Params: {count_parameters(self.model):,} | Device: {self.device}")

    def prepare_data(self, dataset_dir, subjects=None, window_size=200,
                     overlap=100, val_ratio=0.15, test_ratio=0.15, max_files=None):
        """Chuẩn bị DataLoader cho train/val/test."""
        print("\nDang tai du lieu SisFall...")
        X, y = load_raw_windows_for_lstm(dataset_dir, subjects=subjects,
                                         window_size=window_size, overlap=overlap, max_files=max_files)
        print(f"  Tong mau: {len(X)} | Falls: {np.sum(y==1)} | ADLs: {np.sum(y==0)}")

        # Z-score normalization
        mean = X.mean(axis=(0, 1), keepdims=True)
        std = X.std(axis=(0, 1), keepdims=True) + 1e-8
        X = (X - mean) / std
        np.save(self.save_dir / 'norm_mean.npy', mean.squeeze())
        np.save(self.save_dir / 'norm_std.npy', std.squeeze())

        X_tensor = torch.FloatTensor(X)
        y_tensor = torch.LongTensor(y)
        dataset = TensorDataset(X_tensor, y_tensor)

        total = len(dataset)
        test_size = int(total * test_ratio)
        val_size = int(total * val_ratio)
        train_size = total - val_size - test_size

        train_set, val_set, test_set = random_split(
            dataset, [train_size, val_size, test_size],
            generator=torch.Generator().manual_seed(42))

        # Class weights
        train_labels = y[train_set.indices]
        class_counts = np.bincount(train_labels, minlength=2)
        weights = len(train_labels) / (2 * class_counts + 1e-8)
        self.criterion = nn.CrossEntropyLoss(weight=torch.FloatTensor(weights).to(self.device))

        train_loader = DataLoader(train_set, batch_size=self.batch_size, shuffle=True, drop_last=True)
        val_loader = DataLoader(val_set, batch_size=self.batch_size, shuffle=False)
        test_loader = DataLoader(test_set, batch_size=self.batch_size, shuffle=False)
        self.test_loader = test_loader

        print(f"  Train: {len(train_set)} | Val: {len(val_set)} | Test: {len(test_set)}")
        return train_loader, val_loader, test_loader

    def train_epoch(self, train_loader):
        self.model.train()
        total_loss, correct, total = 0, 0, 0
        for bx, by in train_loader:
            bx, by = bx.to(self.device), by.to(self.device)
            self.optimizer.zero_grad()
            out = self.model(bx)
            loss = self.criterion(out, by)
            loss.backward()
            nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            total_loss += loss.item() * bx.size(0)
            correct += out.argmax(1).eq(by).sum().item()
            total += by.size(0)
        return total_loss / total, correct / total

    @torch.no_grad()
    def validate(self, val_loader):
        self.model.eval()
        total_loss, correct, total = 0, 0, 0
        for bx, by in val_loader:
            bx, by = bx.to(self.device), by.to(self.device)
            out = self.model(bx)
            loss = self.criterion(out, by)
            total_loss += loss.item() * bx.size(0)
            correct += out.argmax(1).eq(by).sum().item()
            total += by.size(0)
        return total_loss / total, correct / total

    def train(self, train_loader, val_loader):
        """Vòng lặp huấn luyện chính."""
        print(f"\n{'='*60}\n  TRAINING {self.model_type.upper()}\n{'='*60}")
        best_val_acc, best_epoch = 0, 0
        start = time.time()

        for epoch in range(1, self.num_epochs + 1):
            t0 = time.time()
            train_loss, train_acc = self.train_epoch(train_loader)
            val_loss, val_acc = self.validate(val_loader)
            self.scheduler.step(val_loss)
            lr = self.optimizer.param_groups[0]['lr']

            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_acc'].append(val_acc)
            self.history['lr'].append(lr)

            print(f"  Epoch {epoch:3d}/{self.num_epochs} | "
                  f"TLoss: {train_loss:.4f} TAcc: {train_acc:.4f} | "
                  f"VLoss: {val_loss:.4f} VAcc: {val_acc:.4f} | "
                  f"LR: {lr:.6f} | {time.time()-t0:.1f}s")

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_epoch = epoch
                self.save_checkpoint('best_model.pt', epoch, val_acc, val_loss)

            self.early_stopping(val_loss)
            if self.early_stopping.should_stop:
                print(f"\n  Early stopping at epoch {epoch}")
                break

        elapsed = time.time() - start
        print(f"\n  Done in {elapsed:.1f}s | Best: epoch {best_epoch}, VAcc {best_val_acc:.4f}")

        self.save_checkpoint('final_model.pt', epoch, val_acc, val_loss)
        with open(self.save_dir / f'history_{self.model_type}.json', 'w') as f:
            json.dump(self.history, f, indent=2)

        return self.history

    def save_checkpoint(self, filename, epoch, val_acc, val_loss):
        torch.save({
            'model_type': self.model_type,
            'model_state_dict': self.model.state_dict(),
            'epoch': epoch, 'val_acc': val_acc, 'val_loss': val_loss,
            'input_size': self.input_size,
            'timestamp': datetime.now().isoformat(),
        }, self.save_dir / filename)

    def load_checkpoint(self, filepath):
        ckpt = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(ckpt['model_state_dict'])
        print(f"  Loaded: epoch {ckpt['epoch']}, val_acc {ckpt['val_acc']:.4f}")
        return ckpt


def quick_train(dataset_dir, model_type='lstm', subjects=None, num_epochs=30, max_files=None):
    """Hàm huấn luyện nhanh."""
    pipeline = TrainingPipeline(model_type=model_type, input_size=9, num_epochs=num_epochs)
    train_loader, val_loader, _ = pipeline.prepare_data(dataset_dir, subjects=subjects, max_files=max_files)
    return pipeline.train(train_loader, val_loader)


if __name__ == '__main__':
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATASET_DIR = str(BASE_DIR / 'SisFall_dataset')
    quick_train(DATASET_DIR, model_type='lstm',
                subjects=['SA01', 'SA02', 'SA03', 'SA04', 'SA05'], num_epochs=30)
