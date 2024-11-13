# client_server.py
import json
import threading
import socket
from utils import log_message, send_json_message
import state

def remove_node(node_name):
    state.nodes = [node for node in state.nodes if node["name"] != node_name]

def register_node(client_socket, address, node_name):
    node_info = {
        "name": node_name,
        "host": address[0],
        "port": address[1],
        "models": []
    }
    state.nodes.append({"socket": client_socket, **node_info})
    send_json_message(client_socket, {"type": "SERVER ACK"}, node_name)

def handle_client_message(client_socket, address, message):
    msg_type = message.get("type")
    node_name = message.get("name")
    log_message("RECEIVE", node_name or "Unknown", message)

    if msg_type == "CLIENT CONNECT":
        register_node(client_socket, address, node_name)
    elif msg_type == "CLIENT PING":
        send_json_message(client_socket, {"type": "SERVER PONG"}, node_name)
    elif msg_type == "CLIENT DISCONNECT":
        remove_node(node_name)
        send_json_message(client_socket, {"type": "SERVER ACK"}, node_name)
        return False
    elif msg_type == "JSON_RESPONSE":
        node_name = message.get("name", "Unknown")
        json_data = message.get("data")
        
        if "json_name" in message:
            json_key = f"{node_name}:{message['json_name']}"
        elif "inference_key" in message:
            json_key = message["inference_key"]
        else:
            log_message("ERROR", f"Unknown JSON_RESPONSE format: {message}", "")
            return True  # Continue handling other messages

        state.json_responses[json_key] = json_data
        log_message("RECEIVE", node_name, json_data)
    elif msg_type == "NODE INFO":
        node_name = message["name"]
        models = message.get("models", [])
        state.update_node_models(node_name, models)
        log_message("INFO", f"Updated node info for {node_name}: models={models}", "")
    elif msg_type == "TRAINING_COMPLETED":
        node_name = message.get("name")
        train_key = message.get("train_key")
        model_name = message.get("model_name")
        log_message("INFO", f"Training completed for {model_name}", "")
        state.json_responses[train_key] = message.get("data")
        # also add the new model to state
        print(f"")
        for node in state.nodes:
            if node["name"] == node_name:
                models = node.get("models", [])
                models.append(model_name)
                state.update_node_models(node_name, models)
        print(f"state: {state.nodes}")
    elif msg_type == "NEW MODEL ADDED":
        new_model = message.get("new_model")
        models = message.get("models", [])
        if new_model:
            models.append(new_model)
        log_message("INFO", f"New model '{new_model}' added for node '{node_name}'", "")
        # state.update_node_models(node_name, models)
    else:
        log_message("WARNING", f"Unhandled message type: {msg_type}", "")

    return True

def handle_client(client_socket, address):
    node_name = "Unknown"
    try:
        while True:
            data = client_socket.recv(4096).decode()
            if not data:
                break
            try:
                messages = data.strip().split('\n')  # Handle multiple messages
                for msg in messages:
                    if msg:
                        message = json.loads(msg)
                        node_name = message.get("name", "Unknown")  # Set node_name
                        if not handle_client_message(client_socket, address, message):
                            break
            except json.JSONDecodeError:
                log_message("ERROR", "Invalid message format received.", "")
    except Exception as e:
        log_message("ERROR", f"Error handling client: {e}", "")
    finally:
        client_socket.close()
        remove_node(node_name)


def forward_train_message(target_node, train_message):
    """Forwrads the train message to the first connected node.
    """
    if not state.nodes:
        log_message("ERROR", "No connected nodes available.", "")
        return
    send_json_message(target_node["socket"], train_message, target_node["name"])

def forward_inference_message(target_node, inference_message):
    if not state.nodes:
        log_message("ERROR", "No connected nodes available.", "")
        return
    send_json_message(target_node["socket"], inference_message, target_node["name"])

def start_client_server(host, port):
    state.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    state.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    state.client_socket.bind((host, port))
    state.client_socket.listen()
    log_message("INFO", f"Client server listening on {host}:{port}", "")

    while True:
        try:
            client_conn, address = state.client_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_conn, address))
            client_thread.start()
        except OSError:
            break
