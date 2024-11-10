from flask import Flask, request, jsonify
from flask_cors import CORS
CORS(app)

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def get_status():
    status_token = request.args.get('statusToken')
    pass

@app.route('/nodes', methods=['GET'])
def get_nodes():
    pass

@app.route('/images', methods=['GET'])
def get_images():
    pass

@app.route('/image', methods=['GET'])
def get_image():
    imagePath = request.args.get('imagePath')
    pass

@app.route('/train', methods=['POST'])
def train():
    pass

@app.route('/inference', methods=['POST'])
def inference():
    pass

if __name__ == '__main__':
    app.run(debug=True)