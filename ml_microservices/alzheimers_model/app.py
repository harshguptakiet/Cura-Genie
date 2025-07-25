from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict_alzheimers():
    # Mock prediction logic
    data = request.get_json()
    return jsonify({
        'prediction': 'negative',
        'confidence': 0.92,
        'input': data
    })

if __name__ == '__main__':
    app.run(port=6002, debug=True)
