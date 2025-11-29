import torch
import torch.nn as nn
import numpy as np
import pandas as pd

class ThreatLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, output_size=1):
        super(ThreatLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # x shape: (batch_size, seq_len, input_size)
        out, _ = self.lstm(x)
        # Decode the hidden state of the last time step
        out = self.fc(out[:, -1, :])
        return out

def create_sequences(data, seq_length):
    xs = []
    ys = []
    for i in range(len(data)-seq_length-1):
        x = data[i:(i+seq_length)]
        y = data[i+seq_length]
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

def train_model(df, location, epochs=100):
    """
    Trains an LSTM model for a specific location based on Threat_Level.
    """
    loc_data = df[df['Location'] == location]['Threat_Level'].values.astype(float)
    
    # Normalize data (simple min-max scaling for 1-5 range)
    # We know threat levels are 1-5, so let's scale to 0-1
    scaler_min = 1
    scaler_max = 5
    loc_data_scaled = (loc_data - scaler_min) / (scaler_max - scaler_min)
    
    seq_length = 5
    if len(loc_data_scaled) <= seq_length + 2:
        return None, None # Not enough data

    X, y = create_sequences(loc_data_scaled, seq_length)

    X = torch.from_numpy(X).float().unsqueeze(2) # (batch, seq, feature)
    y = torch.from_numpy(y).float().unsqueeze(1) # (batch, output)

    model = ThreatLSTM()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(X)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
        
    return model, (scaler_min, scaler_max)

def predict_next(model, recent_data, scaler_params):
    """
    Predicts the next threat level given recent data.
    recent_data: list or array of last 'seq_length' threat levels.
    """
    model.eval()
    scaler_min, scaler_max = scaler_params
    
    # Scale input
    recent_data_scaled = (np.array(recent_data) - scaler_min) / (scaler_max - scaler_min)
    
    with torch.no_grad():
        x = torch.from_numpy(recent_data_scaled).float().unsqueeze(0).unsqueeze(2)
        pred = model(x)
        
    # Inverse scale
    pred_val = pred.item() * (scaler_max - scaler_min) + scaler_min
    return max(1, min(5, round(pred_val)))
