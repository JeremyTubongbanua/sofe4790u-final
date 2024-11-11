from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import socket
import json

app = Flask(__name__)
CORS(app)

API_HOST = "127.0.0.1"
API_PORT = 8000

def send_api_message(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as api_socket:
            api_socket.connect((API_HOST, API_PORT))
            api_socket.sendall(json.dumps(message).encode())
            response = api_socket.recv(1024).decode()
            return json.loads(response)
    except Exception as e:
        return {"error": str(e)}

@app.route('/status', methods=['GET'])
def get_status():
    status_token = request.args.get('statusToken')
    file_path = f"{status_token}.txt"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return jsonify({"txt": content})
    return jsonify({"error": "File not found"}), 404

@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = send_api_message({"type": "GET NODES"})
    return jsonify(nodes)

@app.route('/images', methods=['GET'])
def get_images():
    image_files = []
    for root, _, files in os.walk("./images"):
        for file in files:
            if file.endswith((".jpg", ".jpeg", ".png")):
                image_files.append(os.path.join(root, file))
    return jsonify({"images": image_files})

@app.route('/image', methods=['GET'])
def get_image():
    image_path = request.args.get('imagePath')
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    return jsonify({"error": "Image not found"}), 404

@app.route('/train', methods=['POST'])
def train():
    data = request.json
    node = data["node"]
    model_name = data["modelName"]
    model_type = data["modelType"]
    epochs = data["epochs"]
    batch_size = data["batchSize"]
    learning_rate = data["learningRate"]
    message = {
        "type": "API TRAIN",
        "message": {
            "name": model_name,
            "type": model_type,
            "epochs": epochs,
            "batchSize": batch_size,
            "learningRate": learning_rate
        }
    }
    response = send_api_message(message)
    return jsonify(response)

@app.route('/inference', methods=['POST'])
def inference():
    return jsonify({"error": "Inference not implemented"}), 501

if __name__ == '__main__':
    app.run(debug=True)
