# state.py

import os

DEFAULT_HOST = os.getenv("DEFAULT_HOST", "0.0.0.0")
CLIENT_PORT = int(os.getenv("CLIENT_PORT", 8000))
API_PORT = int(os.getenv("API_PORT", 8001))

nodes = []
json_responses = {}
client_socket = None
