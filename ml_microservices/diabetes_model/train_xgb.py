import xgboost as xgb
import pandas as pd
import joblib

# Example: Load data (replace with real data source)
data = pd.read_csv('data/diabetes_train.csv')
X = data.drop('label', axis=1)
y = data['label']

# Train XGBoost model
model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
model.fit(X, y)

# Save model
joblib.dump(model, 'models/diabetes_xgb.pkl')

# Inference example
# X_new = pd.DataFrame([...])
# preds = model.predict_proba(X_new)
