import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class TimeSeriesAnomalyTransformer(nn.Module):
    def __init__(self, d_model=32, nhead=4, num_layers=2, dim_feedforward=64):
        super().__init__()
        # Input feature is just 1 (the time delta), expanding to d_model space for attention
        self.input_projection = nn.Linear(1, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_layers)
        
        # We classify every single timestamp element in the timeline
        self.classifier = nn.Linear(d_model, 1)

    def forward(self, x):
        # x shape: (batch_size, seq_len, 1)
        x = self.input_projection(x)
        x = self.pos_encoder(x)
        
        # The transformer maps the context of the timeline
        x = self.transformer_encoder(x)
        
        # We project the output dimension down to a single True/False probability per node
        out = self.classifier(x)
        return torch.sigmoid(out).squeeze(-1) # shape: (batch_size, seq_len)

def calculate_time_deltas(timestamps_ms):
    """
    Takes a chronological list of timestamps (ms) and calculates the delta in seconds.
    Caps the maximum delta to prevent outlier distortion.
    """
    deltas = []
    if len(timestamps_ms) == 0:
        return deltas
        
    deltas.append(0.0) # First event has 0 delta
    
    for i in range(1, len(timestamps_ms)):
        diff_sec = (timestamps_ms[i] - timestamps_ms[i-1]) / 1000.0
        diff_sec = min(diff_sec, 60.0) # Cap at 60s
        deltas.append(diff_sec)
        
    return deltas
