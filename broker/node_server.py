import socket
import threading
import json
import signal
import sys
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

# Configuration
DEFAULT_HOST = "127.0.0.1"
CLIENT_PORT = 8000
API_PORT = 8001

# Node state
nodes = []
client_socket = None

# Flask API setup
app = Flask(__name__)
CORS(app)

# Logging
def log_message(action, target, message):
    print(f"[LOG] Action: {action}, Target: {target}, Message: {message}")

# Node management
def remove_node(node_name):
    global nodes
    nodes = [node for node in nodes if node["name"] != node_name]

def register_node(client_socket, address, node_name):
    node_info = {
        "name": node_name,
        "host": address[0],
        "port": address[1],
        "models": []
    }
    nodes.append({"socket": client_socket, **node_info})
    send_json_message(client_socket, {"type": "SERVER ACK"}, node_name)

# Message handling
def send_json_message(client_socket, response, target_name=None):
    try:
        message = json.dumps(response)
        client_socket.sendall(message.encode())
        log_message("SEND", target_name or "Unknown", response)
    except Exception as e:
        print(f"Error sending message: {e}")

def handle_client_message(client_socket, address, message):
    msg_type = message["type"]
    node_name = message.get("name")
    log_message("RECEIVE", node_name, message)

    if msg_type == "CLIENT CONNECT":
        register_node(client_socket, address, node_name)
    elif msg_type == "CLIENT PING":
        send_json_message(client_socket, {"type": "SERVER PONG"}, node_name)
    elif msg_type == "CLIENT DISCONNECT":
        remove_node(node_name)
        send_json_message(client_socket, {"type": "SERVER ACK"}, node_name)
        return False
    return True

def forward_train_message(train_message):
    if not nodes:
        print("No connected nodes available.")
        return
    target_node = nodes[0]
    send_json_message(target_node["socket"], {"type": "SERVER TRAIN", "message": train_message}, target_node["name"])

# Client server handler
def handle_client(client_socket, address):
    try:
        while True:
            data = client_socket.recv(4096).decode()
            if not data:
                break
            try:
                message = json.loads(data)
                if not handle_client_message(client_socket, address, message):
                    break
            except json.JSONDecodeError:
                print("Invalid message format received.")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

@app.route('/status', methods=['GET'])
def get_status():
    status_token = request.args.get('statusToken')
    txt_token = request.args.get('txt')

    if txt_token:
        file_path = f"models/{txt_token}/{txt_token}.txt"
    else:
        file_path = f"{status_token}.txt"

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        return jsonify({"txt": content})
    return jsonify({"error": "File not found"}), 404


@app.route('/nodes', methods=['GET'])
def get_nodes():
    node_names = [node["name"] for node in nodes]
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
    return jsonify({"error": "Inference not implemented"}), 501

# Server setup
def signal_handler(sig, frame):
    global client_socket
    print("\nShutting down the server gracefully...")
    if client_socket:
        client_socket.close()
    sys.exit(0)

def start_client_server(host, port):
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.bind((host, port))
    client_socket.listen()
    print(f"Client server listening on {host}:{port}")

    while True:
        try:
            client_conn, address = client_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_conn, address))
            client_thread.start()
        except OSError:
            break

def start_flask_server():
    app.run(host=DEFAULT_HOST, port=API_PORT, debug=True, use_reloader=False)

# Main execution
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    client_thread = threading.Thread(target=start_client_server, args=(DEFAULT_HOST, CLIENT_PORT))
    flask_thread = threading.Thread(target=start_flask_server)

    client_thread.start()
    flask_thread.start()

    client_thread.join()
    flask_thread.join()
