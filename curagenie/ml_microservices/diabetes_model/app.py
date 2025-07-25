from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict_diabetes():
    # Mock prediction logic
    data = request.get_json()
    return jsonify({
        'prediction': 'positive',
        'confidence': 0.85,
        'input': data
    })

if __name__ == '__main__':
    app.run(port=6001, debug=True)
