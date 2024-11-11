# broker

## Sample curl commands

```bash
curl "http://127.0.0.1:8001/nodes"
```

```bash
curl "http://127.0.0.1:8001/images"
```

```bash
curl "http://127.0.0.1:8001/image?imagePath=./images/test/cow/alex-kotomanov-hPs69YaVGig-unsplash.jpg" --output sample.jpg
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
```

```bash
curl "http://127.0.0.1:8001/status?txt=test"
```