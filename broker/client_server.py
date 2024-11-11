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
            log_message("ERROR", f"Unknown JSON_RESPONSE format: {message}")
            return True  # Continue handling other messages

        state.json_responses[json_key] = json_data
        log_message("RECEIVE", node_name, json_data)
    else:
        log_message("WARNING", f"Unhandled message type: {msg_type}")

    return True

def handle_client(client_socket, address):
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
                        if not handle_client_message(client_socket, address, message):
                            break
            except json.JSONDecodeError:
                log_message("ERROR", "Invalid message format received.")
    except Exception as e:
        log_message("ERROR", f"Error handling client: {e}")
    finally:
        client_socket.close()
        remove_node(message.get("name", "Unknown"))

def forward_train_message(train_message):
    if not state.nodes:
        log_message("ERROR", "No connected nodes available.")
        return
    target_node = state.nodes[0]
    send_json_message(target_node["socket"], {"type": "SERVER TRAIN", "message": train_message}, target_node["name"])

def forward_inference_message(inference_message):
    if not state.nodes:
        log_message("ERROR", "No connected nodes available.")
        return
    target_node = state.nodes[0]
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
