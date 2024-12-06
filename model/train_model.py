import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset, DataLoader

# Data preprocessing
def preprocess_data(data):
    # Convert categorical variables to numerical
    data['Vehicle_Class_OLD'] = data['Vehicle_Class']
    data['Transmission_OLD'] = data['Transmission']
    data['Fuel_Type_OLD'] = data['Fuel_Type']
    data['Vehicle_Class'] = pd.Categorical(data['Vehicle_Class']).codes
    data['Transmission'] = pd.Categorical(data['Transmission']).codes
    data['Fuel_Type'] = pd.Categorical(data['Fuel_Type']).codes
    return data

# Custom Dataset class
class VehicleDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
        
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Neural Network Model
class EmissionPredictor(nn.Module):
    def __init__(self, input_dim):
        super(EmissionPredictor, self).__init__()
        self.layer1 = nn.Linear(input_dim, 64)
        self.layer2 = nn.Linear(64, 32)
        self.layer3 = nn.Linear(32, 2)  # 2 outputs: CO2 emissions and fuel consumption
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return x

# Training function
def train_model(model, train_loader, criterion, optimizer, num_epochs):
    model.train()
    for epoch in range(num_epochs):
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()

# Main execution
def main():
    # Load and preprocess data
    data = pd.read_csv('co2_emission_canada.tsv', sep='\t')
    data = preprocess_data(data)
    
    data.to_csv("pin_pointed.csv")
    
    # Prepare features and targets
    X = data[['Vehicle_Class', 'Engine_Size', 'Cylinders', 'Transmission', 'Fuel_Type']].values
    y = data[['CO2_Emissions', 'Fuel_Consumption_Comb']].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale data
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Create data loaders
    train_dataset = VehicleDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    
    # Initialize model
    model = EmissionPredictor(input_dim=5)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    
    # Train model
    train_model(model, train_loader, criterion, optimizer, num_epochs=100)
    
    # Save model
    torch.save(model.state_dict(), 'emission_predictor.pth')

if __name__ == "__main__":
    main()