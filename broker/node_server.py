import socket
import threading
import json
import signal
import sys

DEFAULT_HOST = "127.0.0.1"
CLIENT_PORT = 8000
API_PORT = 8001
nodes = []
client_socket = None
api_socket = None

def log_message(action, target, message):
    print(f"[LOG] Action: {action}, Target: {target}, Message: {message}")

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

def handle_api_message(api_socket):
    try:
        while True:
            data = api_socket.recv(1024).decode()
            if not data:
                break
            try:
                message = json.loads(data)
                if message["type"] == "API TRAIN":
                    log_message("RECEIVE", "API", message)
                    train_message = message["message"]
                    forward_train_message(train_message)
                    send_json_message(api_socket, {"type": "SERVER ACK"})
                elif message["type"] == "GET NODES":
                    node_names = [node["name"] for node in nodes]
                    send_json_message(api_socket, {"nodes": node_names})
            except json.JSONDecodeError:
                print("Invalid API message format received.")
    except Exception as e:
        print(f"Error handling API message: {e}")
    finally:
        api_socket.close()

def handle_client(client_socket, address):
    try:
        while True:
            data = client_socket.recv(1024).decode()
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

def signal_handler(sig, frame):
    global client_socket, api_socket
    print("\nShutting down the server gracefully...")
    if client_socket:
        client_socket.close()
    if api_socket:
        api_socket.close()
    sys.exit(0)

def start_client_server(host, port):
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

def start_api_server(host, port):
    global api_socket
    api_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    api_socket.bind((host, port))
    api_socket.listen()
    print(f"API server listening on {host}:{port}")

    while True:
        try:
            api_conn, _ = api_socket.accept()
            api_thread = threading.Thread(target=handle_api_message, args=(api_conn,))
            api_thread.start()
        except OSError:
            break

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    threading.Thread(target=start_client_server, args=(DEFAULT_HOST, CLIENT_PORT)).start()
    threading.Thread(target=start_api_server, args=(DEFAULT_HOST, API_PORT)).start()
