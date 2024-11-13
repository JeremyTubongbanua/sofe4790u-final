# state.py

import os

HOST = os.getenv("HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))
API_PORT = int(os.getenv("API_PORT", 8001))

nodes = []
json_responses = {}
client_socket = None

def update_node_models(node_name, models):
    for node in nodes:
        if node["name"] == node_name:
            node["models"] = models
            return
    nodes.append({"name": node_name, "models": models})
