"""
Deep Learning Models — FallGuard AI
=====================================================
Kiến trúc mạng LSTM và GRU cho bài toán phân loại hành vi té ngã.

Bao gồm:
  - FallDetectionLSTM: Mạng LSTM 2 lớp với Dropout
  - FallDetectionGRU: Mạng GRU 2 lớp (nhẹ hơn, so sánh)
  - FallDetectionCNNLSTM: Kết hợp 1D-CNN + LSTM (trích xuất cục bộ + thời gian)

Tất cả mô hình nhận đầu vào shape (batch, seq_len, input_size)
và trả về logits shape (batch, num_classes).
"""

import torch
import torch.nn as nn
import numpy as np


class FallDetectionLSTM(nn.Module):
    """
    Mô hình LSTM cho phân loại hành vi té ngã.

    Kiến trúc:
        Input → BatchNorm → LSTM(2 layers, bidirectional) → Dropout → FC → Output

    Args:
        input_size: Số features đầu vào mỗi timestep (9 cho SisFall raw, 108 cho features)
        hidden_size: Kích thước hidden state
        num_layers: Số lớp LSTM xếp chồng
        num_classes: Số lớp đầu ra (2: ADL/Fall)
        dropout: Tỷ lệ dropout
        bidirectional: Sử dụng Bi-LSTM?
    """
    def __init__(self, input_size=9, hidden_size=128, num_layers=2,
                 num_classes=2, dropout=0.3, bidirectional=True):
        super(FallDetectionLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.num_directions = 2 if bidirectional else 1

        # Batch Normalization trên input
        self.bn_input = nn.BatchNorm1d(input_size)

        # LSTM Layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )

        # Attention layer (đơn giản)
        self.attention = nn.Sequential(
            nn.Linear(hidden_size * self.num_directions, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )

        # Fully Connected classifier
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size * self.num_directions, 64),
            nn.ReLU(),
            nn.Dropout(dropout / 2),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: Tensor shape (batch, seq_len, input_size)
        Returns:
            logits: Tensor shape (batch, num_classes)
        """
        batch_size = x.size(0)

        # Batch Norm trên chiều feature (cần reshape)
        x = x.permute(0, 2, 1)  # (batch, features, seq_len)
        x = self.bn_input(x)
        x = x.permute(0, 2, 1)  # (batch, seq_len, features)

        # LSTM forward
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden*directions)

        # Attention mechanism
        attn_weights = self.attention(lstm_out)  # (batch, seq_len, 1)
        attn_weights = torch.softmax(attn_weights, dim=1)
        context = torch.sum(lstm_out * attn_weights, dim=1)  # (batch, hidden*directions)

        # Classify
        out = self.classifier(context)
        return out


class FallDetectionGRU(nn.Module):
    """
    Mô hình GRU — biến thể nhẹ hơn LSTM, ít tham số hơn.
    Dùng để so sánh hiệu năng với LSTM.

    Kiến trúc:
        Input → BatchNorm → GRU(2 layers) → FC → Output
    """
    def __init__(self, input_size=9, hidden_size=128, num_layers=2,
                 num_classes=2, dropout=0.3, bidirectional=True):
        super(FallDetectionGRU, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_directions = 2 if bidirectional else 1

        self.bn_input = nn.BatchNorm1d(input_size)

        self.gru = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )

        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size * self.num_directions, 64),
            nn.ReLU(),
            nn.Dropout(dropout / 2),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        batch_size = x.size(0)

        x = x.permute(0, 2, 1)
        x = self.bn_input(x)
        x = x.permute(0, 2, 1)

        gru_out, _ = self.gru(x)

        # Lấy output cuối cùng
        out = gru_out[:, -1, :]  # (batch, hidden*directions)

        out = self.classifier(out)
        return out


class FallDetectionCNNLSTM(nn.Module):
    """
    Mô hình kết hợp 1D-CNN + LSTM.

    1D-CNN trích xuất đặc trưng cục bộ (local patterns),
    LSTM học phụ thuộc thời gian dài hạn (temporal dependencies).

    Kiến trúc:
        Input → Conv1D(3 layers) → LSTM → FC → Output
    """
    def __init__(self, input_size=9, num_classes=2, dropout=0.3):
        super(FallDetectionCNNLSTM, self).__init__()

        # 1D Convolutional layers
        self.cnn = nn.Sequential(
            nn.Conv1d(input_size, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(128, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
        )

        # LSTM layer
        self.lstm = nn.LSTM(
            input_size=64,
            hidden_size=64,
            num_layers=1,
            batch_first=True,
            bidirectional=True
        )

        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(128, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes)
        )

    def forward(self, x):
        # x: (batch, seq_len, input_size)
        x = x.permute(0, 2, 1)  # (batch, input_size, seq_len)

        # CNN
        cnn_out = self.cnn(x)  # (batch, 64, seq_len/4)

        # Reshape cho LSTM
        cnn_out = cnn_out.permute(0, 2, 1)  # (batch, seq_len/4, 64)

        # LSTM
        lstm_out, _ = self.lstm(cnn_out)

        # Lấy output cuối
        out = lstm_out[:, -1, :]  # (batch, 128)

        out = self.classifier(out)
        return out


class PositionalEncoding(nn.Module):
    """
    Mã hóa vị trí (Positional Encoding) cho Transformer.
    Sử dụng hàm sin/cos để mã hóa thông tin vị trí của mỗi timestep
    trong chuỗi đầu vào, giúp Transformer nhận biết thứ tự thời gian.
    """
    def __init__(self, d_model, max_len=500, dropout=0.1):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        if d_model % 2 == 1:
            pe[:, 1::2] = torch.cos(position * div_term[:-1])
        else:
            pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """x: (batch, seq_len, d_model)"""
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class FallDetectionTransformer(nn.Module):
    """
    Mô hình Transformer Encoder cho phân loại hành vi té ngã.

    Sử dụng cơ chế Self-Attention nhiều đầu (Multi-Head Attention) để
    nắm bắt các phụ thuộc toàn cục (global dependencies) trong chuỗi
    thời gian — ưu điểm vượt trội so với LSTM/GRU ở khả năng xử lý
    song song và quan hệ xa.

    Kiến trúc:
        Input → Linear Projection → Positional Encoding
              → Transformer Encoder (N layers) → Global Average Pooling
              → FC → Output

    Args:
        input_size: Số features đầu vào mỗi timestep (9 cho SisFall raw)
        d_model: Chiều embedding bên trong Transformer
        nhead: Số attention heads
        num_layers: Số lớp Transformer Encoder xếp chồng
        dim_feedforward: Chiều hidden của FFN bên trong mỗi layer
        num_classes: Số lớp đầu ra (2: ADL/Fall)
        dropout: Tỷ lệ dropout
    """
    def __init__(self, input_size=9, d_model=64, nhead=4, num_layers=2,
                 dim_feedforward=128, num_classes=2, dropout=0.3, **kwargs):
        super(FallDetectionTransformer, self).__init__()

        # Linear projection: input_size → d_model
        self.input_projection = nn.Sequential(
            nn.Linear(input_size, d_model),
            nn.LayerNorm(d_model),
            nn.ReLU(),
        )

        # Positional Encoding
        self.pos_encoder = PositionalEncoding(d_model, max_len=500, dropout=dropout)

        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
            activation='gelu',
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )

        # Classifier (Global Average Pooling + FC)
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Dropout(dropout),
            nn.Linear(d_model, 64),
            nn.GELU(),
            nn.Dropout(dropout / 2),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: Tensor shape (batch, seq_len, input_size)
        Returns:
            logits: Tensor shape (batch, num_classes)
        """
        # Project input features to d_model dimension
        x = self.input_projection(x)  # (batch, seq_len, d_model)

        # Add positional encoding
        x = self.pos_encoder(x)

        # Transformer Encoder
        x = self.transformer_encoder(x)  # (batch, seq_len, d_model)

        # Global Average Pooling over time dimension
        x = x.mean(dim=1)  # (batch, d_model)

        # Classify
        out = self.classifier(x)
        return out


class TemporalBlock(nn.Module):
    """
    Một khối TCN (Temporal Block) với dilated causal convolution,
    BatchNorm, ReLU, Dropout, và kết nối tắt (residual connection).

    Dilated convolution cho phép mở rộng receptive field theo cấp số nhân
    mà không tăng số tham số.
    """
    def __init__(self, in_channels, out_channels, kernel_size, dilation, dropout=0.2):
        super(TemporalBlock, self).__init__()
        padding = (kernel_size - 1) * dilation  # causal padding

        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size,
                               padding=padding, dilation=dilation)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size,
                               padding=padding, dilation=dilation)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()

        # Residual connection (downsample if channels change)
        self.downsample = nn.Conv1d(in_channels, out_channels, 1) \
            if in_channels != out_channels else None

        self.padding = padding

    def forward(self, x):
        """x: (batch, channels, seq_len)"""
        residual = x

        out = self.conv1(x)
        out = out[:, :, :x.size(2)]  # Causal: cắt phần tương lai
        out = self.bn1(out)
        out = self.relu(out)
        out = self.dropout(out)

        out = self.conv2(out)
        out = out[:, :, :x.size(2)]  # Causal: cắt phần tương lai
        out = self.bn2(out)
        out = self.relu(out)
        out = self.dropout(out)

        # Residual
        if self.downsample is not None:
            residual = self.downsample(residual)

        return self.relu(out + residual)


class FallDetectionTCN(nn.Module):
    """
    Mô hình TCN (Temporal Convolutional Network) cho phân loại hành vi té ngã.

    TCN sử dụng dilated causal convolutions để xử lý chuỗi thời gian.
    Ưu điểm so với RNN:
      - Huấn luyện song song (parallelizable)
      - Receptive field có thể kiểm soát linh hoạt
      - Gradient ổn định hơn (không vanishing/exploding gradient)
      - Tốc độ inference nhanh

    Kiến trúc:
        Input → [TemporalBlock × N layers (dilation tăng dần)]
              → Global Average Pooling → FC → Output

    Args:
        input_size: Số features đầu vào mỗi timestep (9 cho SisFall raw)
        num_channels: List kích thước kênh cho mỗi TemporalBlock
        kernel_size: Kích thước kernel cho dilated convolution
        num_classes: Số lớp đầu ra (2: ADL/Fall)
        dropout: Tỷ lệ dropout
    """
    def __init__(self, input_size=9, num_channels=None, kernel_size=3,
                 num_classes=2, dropout=0.3, **kwargs):
        super(FallDetectionTCN, self).__init__()

        if num_channels is None:
            num_channels = [32, 64, 64, 32]

        # Input BatchNorm
        self.bn_input = nn.BatchNorm1d(input_size)

        # Stack of TemporalBlocks with exponentially increasing dilation
        layers = []
        num_levels = len(num_channels)
        for i in range(num_levels):
            in_ch = input_size if i == 0 else num_channels[i - 1]
            out_ch = num_channels[i]
            dilation = 2 ** i  # 1, 2, 4, 8, ...
            layers.append(TemporalBlock(in_ch, out_ch, kernel_size, dilation, dropout))

        self.tcn_layers = nn.Sequential(*layers)

        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(num_channels[-1], 32),
            nn.ReLU(),
            nn.Dropout(dropout / 2),
            nn.Linear(32, num_classes),
        )

    def forward(self, x):
        """
        Forward pass.

        Args:
            x: Tensor shape (batch, seq_len, input_size)
        Returns:
            logits: Tensor shape (batch, num_classes)
        """
        # Transpose: (batch, seq_len, features) → (batch, features, seq_len)
        x = x.permute(0, 2, 1)

        # Input normalization
        x = self.bn_input(x)

        # TCN
        x = self.tcn_layers(x)  # (batch, num_channels[-1], seq_len)

        # Global Average Pooling
        x = x.mean(dim=2)  # (batch, num_channels[-1])

        # Classify
        out = self.classifier(x)
        return out


def get_model(model_type: str = 'lstm', **kwargs) -> nn.Module:
    """
    Factory function để tạo model theo tên.

    Args:
        model_type: 'lstm', 'gru', 'cnn_lstm', 'transformer', hoặc 'tcn'
        **kwargs: Tham số truyền vào constructor

    Returns:
        nn.Module instance
    """
    models = {
        'lstm': FallDetectionLSTM,
        'gru': FallDetectionGRU,
        'cnn_lstm': FallDetectionCNNLSTM,
        'transformer': FallDetectionTransformer,
        'tcn': FallDetectionTCN,
    }
    if model_type not in models:
        raise ValueError(f"Model '{model_type}' không hợp lệ. Chọn: {list(models.keys())}")

    # Filter kwargs to only pass what the model constructor accepts
    import inspect
    sig = inspect.signature(models[model_type].__init__)
    valid_params = set(sig.parameters.keys()) - {'self'}
    # If constructor accepts **kwargs, pass everything
    has_var_keyword = any(
        p.kind == inspect.Parameter.VAR_KEYWORD
        for p in sig.parameters.values()
    )
    if has_var_keyword:
        filtered_kwargs = kwargs
    else:
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}

    return models[model_type](**filtered_kwargs)


def count_parameters(model: nn.Module) -> int:
    """Đếm tổng số tham số có thể huấn luyện."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ─── Test ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    import numpy as np

    print("=" * 60)
    print("  Model Architecture Test — FallGuard AI")
    print("=" * 60)

    # Giả lập input: batch=4, seq_len=200, features=9 (SisFall raw)
    dummy = torch.randn(4, 200, 9)

    for name in ['lstm', 'gru', 'cnn_lstm', 'transformer', 'tcn']:
        model = get_model(name, input_size=9)
        output = model(dummy)
        params = count_parameters(model)
        print(f"\n📌 {name.upper()}")
        print(f"   Input:  {dummy.shape}")
        print(f"   Output: {output.shape}")
        print(f"   Params: {params:,}")

    print("\n✅ Tất cả 5 model test thành công!")
