import joblib
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)
model = joblib.load('models/diabetes_xgb.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    X = pd.DataFrame([data['features']])
    proba = model.predict_proba(X)[0][1]
    return jsonify({'risk_score': float(proba)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
