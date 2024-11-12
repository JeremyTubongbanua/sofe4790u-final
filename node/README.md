# ml

## How to Run

1. Unzip `dataset.zip`

2. Run the virtual environment by running `source venv/bin/activate`

3. Use pip to install the required packages by running `venv/bin/pip install -r requirements.txt`

4. Run the program by running

```sh
python3 train.py --data-dir ./images --base-model mobilenet --epochs 2 --batch-size 32 --learning-rate 0.001 --model-save-path models/test/test.pth --report models/test/test.json --output-file models/test/test.txt
```

Choices:

| Base Model     | Argument     |
|----------------|--------------|
| MobileNet      | mobilenet    |
| ResNet50       | resnet       |
| EfficientNet   | efficientnet |

5. Inference

```sh
python3 inference.py --image-path images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg --model-path models/test/test.pth --base-model mobilenet --class-names-path images/classes.txt --report models/test/inference.json
```

## Dockerfile

```bash
sudo docker build -t node .
sudo docker run --rm --name node0 node --host 127.0.0.1 --port 8000 --name node0
sudo docker run --rm -d --name node0 --entrypoint python3 node node_client.py --host 192.168.8.125 --port 8000 --name node0
sudo docker logs -f node0
sudo docker run --rm --name node0 node --host 172.17.0.2 --port 8000 --name node0
```