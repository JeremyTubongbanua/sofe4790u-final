FROM python:3.11-slim

WORKDIR /app

COPY get_dataset.py node_client.py inference.py train.py ./

RUN pip install --upgrade pip
RUN pip install torch torchvision pillow requests

RUN python3 get_dataset.py

ENTRYPOINT ["python3", "node_client.py"]
