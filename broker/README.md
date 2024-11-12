# broker

## Sample curl commands

```bash
curl "http://127.0.0.1:8001/nodes"
curl "http://192.168.8.125:8001/nodes"
```

```bash
curl "http://127.0.0.1:8001/images"
curl "http://192.168.8.125:8001/images"
```

```bash
curl "http://127.0.0.1:8001/image?imagePath=./images/test/cow/alex-kotomanov-hPs69YaVGig-unsplash.jpg" --output sample.jpg
curl "http://192.168.8.125:8001/image?imagePath=./images/test/cow/alex-kotomanov-hPs69YaVGig-unsplash.jpg" --output sample.jpg
```

```bash
curl -X POST "http://127.0.0.1:8001/train" \
-H "Content-Type: application/json" \
-d '{
  "node": "node0",
  "modelName": "test",
  "modelType": "mobilenet",
  "epochs": 1,
  "batchSize": 32,
  "learningRate": 0.001
}'
curl -X POST "http://192.168.8.125:8001/train" \
-H "Content-Type: application/json" \
-d '{
  "node": "node0",
  "modelName": "test",
  "modelType": "mobilenet",
  "epochs": 1,
  "batchSize": 32,
  "learningRate": 0.001
}'
```

```bash
curl "http://127.0.0.1:8001/get_json?node=node2&json=test"
curl "http://192.168.8.125:8001/get_json?node=node0&json=test"
```

```bash
curl -X POST http://127.0.0.1:8001/inference -H "Content-Type: application/json" -d '{
  "node": "node1",
    "imagePath": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
    "modelPath": "models/test/test.pth",
    "baseModel": "mobilenet",
    "classNamesPath": "images/classes.txt",
    "reportPath": "models/test/inference1.json"
}'
curl -X POST http://192.168.8.125:8001/inference -H "Content-Type: application/json" -d '{
  "node": "node0",
    "imagePath": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
    "modelPath": "models/test/test.pth",
    "baseModel": "mobilenet",
    "classNamesPath": "images/classes.txt",
    "reportPath": "models/test/inference1.json"
}'
```

```bash
sudo docker build -t broker .
sudo docker run --rm --name broker -p 8000:8000 -p 8001:8001 broker
```