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

def log_message(action, message):
    print(f"[LOG] Action: {action}, Message: {message}")

def send_json_message(client_socket, message):
    try:
        json_message = json.dumps(message).encode()
        client_socket.sendall(json_message)
        log_message("SEND", message)
    except Exception as e:
        print(f"Error sending message: {e}")

def notify_termination(host, port, name):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        message = {"type": "CLIENT DISCONNECT", "name": name}
        send_json_message(client_socket, message)
        response = client_socket.recv(1024)
        response_data = json.loads(response.decode())
        log_message("RECEIVE", response_data)
        if response_data.get("type") == "SERVER ACK":
            print("Disconnected successfully.")

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
    model_name = train_message["name"]
    base_model = train_message["type"]
    epochs = train_message["epochs"]
    batch_size = train_message["batchSize"]
    learning_rate = train_message["learningRate"]

    output_file = f"models/{model_name}/{model_name}.txt"
    model_save_path = f"models/{model_name}/{model_name}.pth"
    report_path = f"models/{model_name}/{model_name}.json"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Start a thread to monitor the log file
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

def handle_train_request(train_message):
    threading.Thread(target=run_training_process, args=(train_message,), daemon=True).start()

def handle_server_message(client_socket, message):
    msg_type = message["type"]

    if msg_type == "SERVER TRAIN":
        log_message("RECEIVE", message)
        train_message = message["message"]
        handle_train_request(train_message)
        response = {"type": "CLIENT TRAIN STARTED", "message": train_message["name"]}
        send_json_message(client_socket, response)

    elif msg_type == "GET_JSON":
        json_name = message["json_name"]
        node_name = message["name"]
        file_path = f"models/{json_name}/{json_name}.json"

        if not os.path.exists(file_path):
            response = {"type": "ERROR", "name": node_name, "json_name": json_name, "message": f"File '{file_path}' not found"}
        else:
            with open(file_path, "r") as f:
                json_data = json.load(f)
            response = {"type": "JSON_RESPONSE", "name": node_name, "json_name": json_name, "data": json_data}

        send_json_message(client_socket, response)



def start_client(host, port, name):
    def signal_handler(sig, frame):
        notify_termination(host, port, name)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        connect_message = {"type": "CLIENT CONNECT", "name": name}
        send_json_message(client_socket, connect_message)
        response = client_socket.recv(1024)
        response_data = json.loads(response.decode())
        log_message("RECEIVE", response_data)
        if response_data.get("type") != "SERVER ACK":
            return

        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                message = json.loads(data)
                handle_server_message(client_socket, message)
            except json.JSONDecodeError:
                print("Invalid message format received.")
            except Exception as e:
                print(f"Error handling server message: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a client node.")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--name", required=True, help="Node name (e.g., node0)")

    args = parser.parse_args()
    start_client(args.host, args.port, args.name)
