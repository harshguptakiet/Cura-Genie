import xgboost as xgb
import pandas as pd
import joblib

data = pd.read_csv('data/alzheimers_train.csv')
X = data.drop('label', axis=1)
y = data['label']

model = xgb.XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1)
model.fit(X, y)

joblib.dump(model, 'models/alzheimers_xgb.pkl')
