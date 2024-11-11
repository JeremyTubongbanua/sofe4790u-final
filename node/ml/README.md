# ml

## How to Run

1. Unzip `images.zip`

2. Run the virtual environment by running `source venv/bin/activate`

3. Use pip to install the required packages by running `venv/bin/pip install -r requirements.txt`

4. Run the program by running

```sh
python3 train.py --data-dir ./images --base-model mobilenet --epochs 3 --batch-size 32 --learning-rate 0.001 --report my_custom_model_report.json --model-save-path my_custom_model.pth
```

Choices:

| Base Model     | Argument     |
|----------------|--------------|
| MobileNet      | mobilenet    |
| ResNet50       | resnet       |
| EfficientNet   | efficientnet |

5. Inference

```sh
python3 inference.py --image-path images/test/cow/jim-mIuqj6OfAhs-unsplash.jpg --model-path my_custom_model.pth --base-model mobilenet --class-names-path classes.txt --report inference_report.json
```
