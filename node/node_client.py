import socket
import argparse
import json
import signal
import sys

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

def start_client(host, port, name):
    def signal_handler(sig, frame):
        notify_termination(host, port, name)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        # Register the client
        connect_message = {"type": "CLIENT CONNECT", "name": name}
        send_json_message(client_socket, connect_message)
        response = client_socket.recv(1024)
        response_data = json.loads(response.decode())
        log_message("RECEIVE", response_data)
        if response_data.get("type") == "SERVER ACK":
            print(f"Connected to server as {name}.")

        # Ping server
        ping_message = {"type": "CLIENT PING"}
        send_json_message(client_socket, ping_message)
        response = client_socket.recv(1024)
        response_data = json.loads(response.decode())
        log_message("RECEIVE", response_data)
        if response_data.get("type") == "SERVER PONG":
            print("Received PONG from server.")

        # Keep the connection open
        signal.pause()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a client node.")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--name", required=True, help="Node name (e.g., node0)")

    args = parser.parse_args()
    start_client(args.host, args.port, args.name)
