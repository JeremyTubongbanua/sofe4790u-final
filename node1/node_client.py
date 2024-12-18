# node_client.py

import socket
import argparse
import json
import signal
import sys
import subprocess
import os
import threading
import time

log_cache = {}
log_cache_lock = threading.Lock()
client_socket = None

def get_models():
    models_dir = "models"
    if not os.path.exists(models_dir):
        return []
    return [name for name in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, name))]

def send_node_info():
    global client_socket
    models = get_models()
    message = {
        "type": "NODE INFO",
        "name": args.name,
        "models": models
    }
    send_json_message(message)

def log_message(action, message):
    print(f"[LOG] Action: {action}, Message: {message}")

def send_json_message(message):
    global client_socket
    try:
        json_message = (json.dumps(message) + '\n').encode()
        client_socket.sendall(json_message)
        log_message("SEND", message)
    except Exception as e:
        print(f"Error sending message: {e}")

def notify_new_model(model_name):
    models = get_models()
    message = {
        "type": "NEW MODEL ADDED",
        "name": args.name,
        "new_model": model_name,
        "models": models
    }
    send_json_message(message)
    log_message("INFO", f"Notified server of new model: {model_name}")

def notify_termination(host, port, name):
    global client_socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
            temp_socket.connect((host, port))
            message = {"type": "CLIENT DISCONNECT", "name": name}
            json_message = json.dumps(message).encode()
            temp_socket.sendall(json_message)
            response = temp_socket.recv(1024)
            response_data = json.loads(response.decode())
            log_message("RECEIVE", response_data)
            if response_data.get("type") == "SERVER ACK":
                print("Disconnected successfully.")
    except Exception as e:
        print(f"Error during termination notification: {e}")

def monitor_log_file(model_name):
    file_path = f"models/{model_name}/{model_name}.txt"
    if not os.path.exists(file_path):
        return
    with open(file_path, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            where = f.tell()
            line = f.readline()
            if not line:
                time.sleep(0.1)
                f.seek(where)
            else:
                with log_cache_lock:
                    if model_name not in log_cache:
                        log_cache[model_name] = []
                    log_cache[model_name].append(line.strip())
                    log_cache[model_name] = log_cache[model_name][-100:]

def run_training_process(train_message):
    model_name = train_message["modelName"]
    base_model = train_message["modelType"]
    epochs = train_message["epochs"]
    batch_size = train_message["batchSize"]
    learning_rate = train_message["learningRate"]
    train_key = train_message["train_key"]
    output_file = f"models/{model_name}/{model_name}.txt"
    model_save_path = f"models/{model_name}/{model_name}.pth"
    report_path = f"models/{model_name}/{model_name}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    threading.Thread(target=monitor_log_file, args=(model_name,), daemon=True).start()
    command = [
        "python3", "train.py",
        "--data-dir", "./images",
        "--base-model", base_model,
        "--epochs", str(epochs),
        "--batch-size", str(batch_size),
        "--learning-rate", str(learning_rate),
        "--model-save-path", model_save_path,
        "--report", report_path,
        "--output-file", output_file
    ]
    log_message("INFO", f"Starting training subprocess: {' '.join(command)}")
    with open(output_file, "w") as f:
        process = subprocess.Popen(command, stdout=f, stderr=subprocess.STDOUT)
        process.wait()
    log_message("INFO", f"Training completed for model: {model_name}")
    with open(output_file, "r") as f:
        output_contents = f.read()
    response = {
        "type": "TRAINING_COMPLETED",
        "name": args.name,
        "train_key": train_key,
        "model_name": model_name,
        "data": {
            "model_path": model_save_path,
            "report_path": report_path,
            "output_file": output_file,
            "output_contents": output_contents
        }
    }
    send_json_message(response)
    notify_new_model(model_name)

def run_inference_process(inference_message):
    global client_socket

    print(f"Running inference process")

    image_path = inference_message["image_path"]
    model_name = inference_message["model_name"]
    train_report_path = f"models/{model_name}/{model_name}.json"
    # print(f"train_report_path: {train_report_path}")
    # print(f"model_name: {model_name}")
    # print(f"image_path: {image_path}")
    # read report_path for the base_model, class_names_path, and the model_path
    with open(train_report_path, "r") as f:
        report = json.load(f)
    model_path = report["model_save_path"]
    base_model = report["arguments"]["base_model"]
    class_names_path = report["arguments"]["data_dir"] + "/classes.txt"
    # base_model = inference_message["base_model"]
    # class_names_path = inference_message["class_names_path"]
    report_path = f"models/{model_name}/{inference_message['inference_key']}.json"

    # lo all variables
    # print(f"image_path: {image_path}")
    # print(f"model_path: {model_path}")
    # print(f"base_model: {base_model}")
    # print(f"class_names_path: {class_names_path}")
    # print(f"train_report_path: {train_report_path}")
    # print(f"report_path: {report_path}")



    command = [
        "python3", "inference.py",
        "--image-path", image_path,
        "--model-path", model_path,
        "--base-model", base_model,
        "--class-names-path", class_names_path,
        "--report", report_path
    ]
    log_message("INFO", f"Starting inference subprocess: {' '.join(command)}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            inference_result = json.load(f)
        response = {
            "type": "JSON_RESPONSE",
            "inference_key": inference_message["inference_key"],
            "data": inference_result
        }
    else:
        response = {
            "type": "ERROR",
            "message": "Inference report not found",
            "inference_key": inference_message["inference_key"]
        }
    send_json_message(response)

def handle_train_request(train_message):
    threading.Thread(target=run_training_process, args=(train_message,), daemon=True).start()

def handle_inference_request(inference_message):
    threading.Thread(target=run_inference_process, args=(inference_message,), daemon=True).start()

def handle_server_message(message):
    msg_type = message.get("type")
    if msg_type == "SERVER TRAIN":
        log_message("RECEIVE", message)
        train_message = message
        if train_message:
            handle_train_request(train_message)
    elif msg_type == "GET_JSON":
        json_name = message.get("json_name")
        node_name = message.get("name")
        file_path = f"models/{json_name}/{json_name}.json"
        if not os.path.exists(file_path):
            response = {
                "type": "ERROR",
                "name": node_name,
                "json_name": json_name,
                "message": f"File '{file_path}' not found"
            }
        else:
            with open(file_path, "r") as f:
                json_data = json.load(f)
            response = {
                "type": "JSON_RESPONSE",
                "name": node_name,
                "json_name": json_name,
                "data": json_data
            }
        send_json_message(response)
    elif msg_type == "SERVER INFERENCE":
        log_message("RECEIVE", message)
        inference_message = message
        handle_inference_request(inference_message)

def start_client(host, port, name):
    global client_socket
    def signal_handler(sig, frame):
        notify_termination(host, port, name)
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        connect_message = {"type": "CLIENT CONNECT", "name": name}
        send_json_message(connect_message)
        send_node_info()
        response = client_socket.recv(1024)
        if response:
            response_data = json.loads(response.decode())
            log_message("RECEIVE", response_data)
            if response_data.get("type") != "SERVER ACK":
                print("Failed to connect to server.")
                return
        while True:
            try:
                data = client_socket.recv(4096).decode()
                if not data:
                    break
                messages = data.strip().split('\n')
                for msg in messages:
                    if msg:
                        message = json.loads(msg)
                        handle_server_message(message)
            except json.JSONDecodeError:
                print("Invalid message format received.")
            except Exception as e:
                print(f"Error handling server message: {e}")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        if client_socket:
            client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a client node.")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--name", required=True, help="Node name (e.g., node0)")
    args = parser.parse_args()
    start_client(args.host, args.port, args.name)
