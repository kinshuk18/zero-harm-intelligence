import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import os

# Explicit execution hardware selection fallback
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🖥️ Execution hardware status: Utilizing {device.type.upper()} for inference layers.")

class SCADADataset(Dataset):
    def __init__(self, features, labels):
        self.features = torch.tensor(features, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]

class CompoundRiskNet(nn.Module):
    def __init__(self, input_dim):
        super(CompoundRiskNet, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)

def train_model():
    # Resolve absolute paths to resource files robustly
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, "data", "raw", "simulated_scada_logs.csv")
    model_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"SCADA engine requires source data. Missing resource at: {data_path}")

    df = pd.read_csv(data_path)
    
    feature_cols = [
        'gas_pressure_psi', 
        'methane_ppm', 
        'temperature_c', 
        'hot_work_permit_active', 
        'confined_space_entry'
    ]
    X = df[feature_cols].values
    y = df['critical_risk_flag'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    train_dataset = SCADADataset(X_train_scaled, y_train)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    input_dim = len(feature_cols)
    model = CompoundRiskNet(input_dim).to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epochs = 20
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for batch_features, batch_labels in train_loader:
            batch_features = batch_features.to(device)
            batch_labels = batch_labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_features)
            loss = criterion(outputs, batch_labels)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            
        if (epoch + 1) % 5 == 0:
            print(f"⚙️ Progress Check: Epoch {epoch+1:02d}/{epochs} | Step Aggregation Loss: {epoch_loss/len(train_loader):.4f}")

    # Serialize tracking artifacts directly to runtime directory
    torch.save(model.state_dict(), os.path.join(model_dir, 'risk_model.pth'))
    np.save(os.path.join(model_dir, 'scaler_mean.npy'), scaler.mean_)
    np.save(os.path.join(model_dir, 'scaler_scale.npy'), scaler.scale_)
    print("💾 Operational arrays and network configurations serialized successfully.")

if __name__ == "__main__":
    train_model()