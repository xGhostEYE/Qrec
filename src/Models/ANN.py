from joblib import dump, load
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler

class QrecPredictor(nn.Module):
    def __init__(self):
        super(QrecPredictor, self).__init__()
        self.fc1 = nn.Linear(4, 8)  # 4 features, 8 neurons in first hidden layer
        self.fc2 = nn.Linear(8, 8) # 8 neurons in second hidden layer
        self.output = nn.Linear(8, 1) # Output layer

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = torch.sigmoid(self.output(x))
        return x

def RunANN(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=42)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = QrecPredictor()
    # Binary Cross Entropy Loss
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    epochs = 100
    for epoch in range(epochs):
        # Convert arrays to tensors
        inputs = torch.tensor(X_train, dtype=torch.float32)
        labels = torch.tensor(y_train, dtype=torch.float32)

        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, labels.unsqueeze(1))

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if (epoch+1) % 10 == 0:
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
    torch.save(model.state_dict(), './ANN_model.pth')
    # dump(model.state_dict(), './ANN_model.joblib')
    # with torch.no_grad():
    #     y_predicted = model(torch.tensor(X_test, dtype=torch.float32))
    #     y_predicted_cls = y_predicted.round()
    #     acc = y_predicted_cls.eq(torch.tensor(y_test).unsqueeze(1)).sum() / float(y_test.shape[0])
    #     print(f'Accuracy: {acc:.4f}')

    
