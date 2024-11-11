from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import os
import time
import state
from utils import send_json_message, log_message
from client_server import forward_train_message

app = Flask(__name__)
CORS(app)

@app.route('/get_json', methods=['GET'])
def get_json():
    node_name = request.args.get("node")
    json_name = request.args.get("json")
    if not node_name or not json_name:
        return jsonify({"error": "Missing 'node' or 'json' parameter"}), 400
    json_key = f"{node_name}:{json_name}"
    target_node = next((node for node in state.nodes if node["name"] == node_name), None)
    if not target_node:
        return jsonify({"error": f"Node '{node_name}' not found"}), 404
    send_json_message(target_node["socket"], {
        "type": "GET_JSON",
        "name": node_name,
        "json_name": json_name
    }, node_name)
    timeout = 5
    start_time = time.time()
    while time.time() - start_time < timeout:
        if json_key in state.json_responses:
            json_data = state.json_responses.pop(json_key)
            return jsonify(json_data)
        time.sleep(0.1)
    return jsonify({"error": "Timeout waiting for client response"}), 504

@app.route('/nodes', methods=['GET'])
def get_nodes():
    node_names = [node["name"] for node in state.nodes]
    return jsonify({"nodes": node_names})

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
    model_name = data["modelName"]
    model_type = data["modelType"]
    epochs = data["epochs"]
    batch_size = data["batchSize"]
    learning_rate = data["learningRate"]
    train_message = {
        "name": model_name,
        "type": model_type,
        "epochs": epochs,
        "batchSize": batch_size,
        "learningRate": learning_rate
    }
    forward_train_message(train_message)
    return jsonify({"status": "Training initiated"})

@app.route('/inference', methods=['POST'])
def inference():
    data = request.json
    node_name = data.get("node")
    image_path = data["imagePath"]
    model_path = data["modelPath"]
    base_model = data["baseModel"]
    class_names_path = data["classNamesPath"]
    report_path = data["reportPath"]
    inference_key = f"inference:{int(time.time()*1000)}"
    inference_message = {
        "type": "SERVER INFERENCE",
        "inference_key": inference_key,
        "image_path": image_path,
        "model_path": model_path,
        "base_model": base_model,
        "class_names_path": class_names_path,
        "report_path": report_path
    }
    target_node = next((node for node in state.nodes if node["name"] == node_name), None)
    if not target_node:
        return jsonify({"error": f"Node '{node_name}' not found"}), 404
    send_json_message(target_node["socket"], inference_message, target_node["name"])
    timeout = 10
    start_time = time.time()
    while time.time() - start_time < timeout:
        if inference_key in state.json_responses:
            inference_result = state.json_responses.pop(inference_key)
            return jsonify(inference_result)
        time.sleep(0.1)
    return jsonify({"error": "Timeout waiting for inference response"}), 504

