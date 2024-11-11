FROM python:3.11-slim

WORKDIR /app

COPY get_dataset.py api.py client_server.py node_server.py state.py utils.py ./

RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install flask flask-cors requests

RUN python3 get_dataset.py

EXPOSE 8000 8001

ENTRYPOINT ["python3", "node_server.py"]
