import numpy as np
from sklearn.linear_model import LogisticRegression

# Dummy training data (simulate fraud behavior)
X = np.array([
    [1000, 5, 60, 40],
    [50000, 20, 90, 85],
    [200, 1, 20, 10],
    [100000, 50, 95, 90],
    [700, 3, 40, 30],
])

y = np.array([0, 1, 0, 1, 0])  # 1 = Fraud, 0 = Normal

model = LogisticRegression()
model.fit(X, y)


def predict_fraud(data):
    probability = model.predict_proba([data])[0][1]
    return float(probability)