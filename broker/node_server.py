# node_server.py

import threading
import signal
import sys
import client_server
import api
import state

def signal_handler(sig, frame):
    print("\nShutting down the server gracefully...")
    if state.client_socket:
        state.client_socket.close()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    client_thread = threading.Thread(target=client_server.start_client_server, args=(state.HOST, state.SERVER_PORT))
    flask_thread = threading.Thread(target=api.app.run, kwargs={"host": state.HOST, "port": state.API_PORT, "debug": True, "use_reloader": False})
    client_thread.start()
    flask_thread.start()
    client_thread.join()
    flask_thread.join()
