# utils.py

import json

def log_message(action, target, message):
    print(f"[LOG] Action: {action}, Target: {target}, Message: {message}")

def send_json_message(client_socket, response, target_name=None):
    try:
        message = json.dumps(response) + '\n'  # Add newline delimiter
        client_socket.sendall(message.encode())
        log_message("SEND", target_name or "Unknown", response)
    except Exception as e:
        print(f"Error sending message: {e}")
