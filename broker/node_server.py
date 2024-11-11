import socket
import threading
import json
import signal
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
nodes = []
server_socket = None

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
    nodes.append(node_info)
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
    global server_socket
    print("\nShutting down the server gracefully...")
    if server_socket:
        server_socket.close()
    sys.exit(0)

def start_server(host, port):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server listening on {host}:{port}")

    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        try:
            client_socket, address = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, address)).start()
        except OSError:
            break  # Socket closed, exit the loop

if __name__ == "__main__":
    start_server(DEFAULT_HOST, DEFAULT_PORT)
