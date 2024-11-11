FROM python:3.11-slim

WORKDIR /app

COPY api.py client_server.py node_server.py state.py utils.py ./

COPY ../get_dataset.py ./

RUN pip install flask flask-cors requests

RUN python3 get_dataset.py

EXPOSE 8000 8001

ENTRYPOINT ["python3", "node_server.py"]
