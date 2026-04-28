import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from model import TimeSeriesAnomalyTransformer
import random

print("Generating Time-Series Structural Dataset...")

seq_len = 30
num_samples = 3000

X_data = []
Y_data = []

# Generate synthetic timelines
for _ in range(num_samples):
    sequence = []
    labels = []
    
    # 60% chance to embed a swarm burst
    has_burst = random.random() > 0.4
    burst_start = random.randint(5, seq_len - 15) if has_burst else -1
    burst_length = random.randint(10, 15)
    
    for i in range(seq_len):
        if has_burst and burst_start <= i < burst_start + burst_length:
            # SWARM: Unnaturally fast, sub-second intervals
            gap = random.uniform(0.01, 0.1)
            label = 1.0
        else:
            # ORGANIC: Human pace, 1 second up to 60 seconds
            gap = random.uniform(1.0, 60.0)
            label = 0.0
            
        sequence.append([gap])
        labels.append(label)
        
    X_data.append(sequence)
    Y_data.append(labels)

X = torch.tensor(X_data, dtype=torch.float32) # (batch, seq_len, 1)
Y = torch.tensor(Y_data, dtype=torch.float32) # (batch, seq_len)

dataset = TensorDataset(X, Y)
dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

model = TimeSeriesAnomalyTransformer()
optimizer = optim.Adam(model.parameters(), lr=0.005)
criterion = nn.BCELoss()

print("Training Time-Series Transformer...")
for epoch in range(12):
    total_loss = 0
    correct = 0
    total_points = 0
    
    for batch_x, batch_y in dataloader:
        optimizer.zero_grad()
        out = model(batch_x) # (batch, seq_len)
        loss = criterion(out, batch_y)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
        preds = (out >= 0.5).float()
        correct += (preds == batch_y).sum().item()
        total_points += batch_y.numel()
        
    acc = correct / total_points
    print(f"Epoch {epoch+1}/12 || Loss: {total_loss/len(dataloader):.4f} || Point Accuracy: {acc*100:.2f}%")

torch.save(model.state_dict(), "model.pth")
print("Training Complete! Time-Series weights saved to model.pth")


