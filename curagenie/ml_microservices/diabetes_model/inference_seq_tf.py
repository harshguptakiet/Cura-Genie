import tensorflow as tf
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)
model = tf.keras.models.load_model('models/diabetes_seq_tf.h5')

@app.route('/predict_seq', methods=['POST'])
def predict_seq():
    data = request.get_json()
    X = np.array(data['features']).reshape(1, -1)
    proba = float(model.predict(X)[0][0])
    return jsonify({'risk_score': proba})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
