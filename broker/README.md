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
➜  sofe4790u-final git:(main) ✗ curl "http://192.168.8.125:8001/images"
{
  "images": [
    "./images/test/chicken/pexels-simaomoreira-21287707.jpg",
    ...
  ]
}
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
curl "http://192.168.8.125:8001/get_json?node=node0&json=test123"
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
    "reportPath": "models/test/inference.json"
}'
```

```bash
sudo docker build -t broker .
sudo docker run --rm --name broker -p 8000:8000 -p 8001:8001 broker
```

Example of curl commands

```
jeremy@school:~/GitHub/sofe4790u-final/node$ curl "ht33;Bcurl "http://192.168.8.125:8001/images"
{
  "images": [
    "./images/test/chicken/pexels-simaomoreira-21287707.jpg",
    ...
    "./images/train/cow/pexels-katlovessteve-735969.jpg"
  ]
}
s
jeremy@school:~/GitHub/sofe4790u-final/node$ curl "http://192.168.8.125:8001/nodes"
{
  "nodes": [
    {
      "models": [
        "test"
      ],
      "name": "node0"
    }
  ]
}

jeremy@school:~/GitHub/sofe4790u-final/node$ cum$ curl "http://192.168.8.125:8001/image?imagePath=./images/test/cow/alex-kotomanov-hPs69YaVGig-unsplash.jpg" --output sample.jpg
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-100 80246  100 80246    0     0  48.3M      0 --:--:-- --:--:-- --:--:-- 76.5M

jeremy@school:~/GitHub/sofe4790u-final/node$ curl -X POST "http://192.168.8.125:8001/train" -H "Content-Type: application/json" \
-d '{
  "node": "node0",
  "modelName": "test",
  "modelType": "mobilenet",
  "epochs": 1,
  "batchSize": 32,
  "learningRate": 0.001
}'
{
  "status": "Training initiated"
}

jeremy@school:~/GitHub/sofe4790u-final/node$ 00m$ curl "http://192.168.8.125:8001/get_json?node=node0&json=test"
{
  "error": "Timeout waiting for client response"
}

jeremy@school:~/GitHub/sofe4790u-final/node$ 00m$ curl "http://192.168.8.125:8001/get_json?node=node0&json=test"
{
  "arguments": {
    "base_model": "mobilenet",
    "batch_size": 32,
    "data_dir": "./images",
    "epochs": 1,
    "learning_rate": 0.001,
    "model_save_path": "models/test/test.pth",
    "output_file": "models/test/test.txt",
    "report": "models/test/test.json"
  },
  "epochs": 1,
  "model_save_path": "/home/jeremy/GitHub/sofe4790u-final/node/models/test/test.pth",
  "results": [
    {
      "epoch": 1,
      "epoch_time_seconds": 17.8977,
      "test_accuracy": 77.0833,
      "test_loss": 0.6187,
      "train_accuracy": 80.1075,
      "train_loss": 0.5539
    }
  ],
  "timestamp": "2024-11-12T00:58:41.198809",
  "total_training_time": 17.898
}

jeremy@school:~/GitHub/sofe4790u-final/node$ curl -X POST http://192.168.8.125:8001/inference -H "Content-Type: application/json" -d '{
  "node": "node0",
  "imagePath": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
  "modelPath": "models/test123/test123.pth",
  "baseModel": "mobilenet",
  "classNamesPath": "images/classes.txt",
  "reportPath": "models/test123/inference.json"
}'
{
  "arguments": {
    "base_model": "mobilenet",
    "class_names_path": "images/classes.txt",
    "image_path": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
    "model_path": "models/test/test.pth",
    "report": "models/test/inference.json"
  },
  "image": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
  "output": [
    [
      "cow",
      1.0
    ],
    [
      "dog",
      9.915651170864398e-20
    ],
    [
      "chicken",
      5.000828460822457e-23
    ]
  ],
  "predicted_class": "cow",
  "timestamp": "2024-11-12T01:03:04.905899"
}

```

curl -X POST http://192.168.8.125:8001/inference -H "Content-Type: application/json" -d '{
  "node": "node0",
  "imagePath": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
  "modelName": "test123"
}'

## Train

Train curl command
```bash
curl -X POST "http://192.168.8.125:8001/train" -H "Content-Type: application/json" -d '{
  "node": "node0",
  "modelName": "test",
  "modelType": "mobilenet",
  "epochs": 1,
  "batchSize": 32,
  "learningRate": 0.001
}'
```

Result

```json
{
  "model_path": "models/test/test.pth",
  "output_contents": "Epoch [1/1], Train Loss: 0.6373, Train Accuracy: 73.12%, Test Loss: 0.0836, Test Accuracy: 95.83%, Epoch Time: 17.81 seconds\nModel saved as /home/jeremy/GitHub/sofe4790u-final/node/models/test/test.pth\nTotal training time: 17.81 seconds\nReport saved to models/test/test.json\n",
  "output_file": "models/test/test.txt",
  "report_path": "models/test/test.json"
}
```

## Inference

Inference curl command
```bash
curl -X POST http://192.168.8.125:8001/inference -H "Content-Type: application/json" -d '{
  "node": "node0",
  "imagePath": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
  "modelName": "test123"
}'
```

```json
{
  "arguments": {
    "base_model": "resnet",
    "class_names_path": "./images/classes.txt",
    "image_path": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
    "model_path": "/home/jeremy/GitHub/sofe4790u-final/node/models/test123/test123.pth",
    "report": "models/test123/inference:1731472926551.json"
  },
  "image": "images/test/cow/illiya-vjestica-PCf58A5427A-unsplash.jpg",
  "output": [
    [
      "dog",
      1.0
    ],
    [
      "cow",
      5.045334379527376e-18
    ],
    [
      "chicken",
      0.0
    ]
  ],
  "predicted_class": "dog",
  "timestamp": "2024-11-13T04:42:08.992004"
}
```


