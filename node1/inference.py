import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import argparse
import json
import datetime

def get_model(base_model, num_classes, model_path):
    if base_model == "mobilenet":
        model = models.mobilenet_v2()
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif base_model == "efficientnet":
        model = models.efficientnet_b0()
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif base_model == "resnet":
        model = models.resnet18()
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:
        raise ValueError("Invalid base model. Choose from: mobilenet, efficientnet, resnet.")

    model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
    model.eval()
    return model

def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = Image.open(image_path).convert("RGB")
    return transform(image).unsqueeze(0)

def predict(image_path, model, class_names):
    image = preprocess_image(image_path)
    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
        predicted_index = torch.argmax(probabilities).item()
        predicted_class = class_names[predicted_index]

        results = [(class_names[i], prob.item()) for i, prob in enumerate(probabilities)]
        results.sort(key=lambda x: x[1], reverse=True)

    return predicted_class, results

def generate_report(report_path, args, image_path, prediction, results):
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "arguments": vars(args),
        "image": image_path,
        "predicted_class": prediction,
        "output": results
    }
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=4)

def main(image_path, model_path, base_model, class_names_path, report_path=None):
    with open(class_names_path, "r") as f:
        class_names = [line.strip() for line in f]

    model = get_model(base_model, len(class_names), model_path)
    predicted_class, results = predict(image_path, model, class_names)

    print(f"Predicted Class: {predicted_class}")
    print("Class Probabilities:")
    for class_name, probability in results:
        print(f"{class_name}: {probability:.2%}")

    if report_path:
        generate_report(report_path, args, image_path, predicted_class, results)
        print(f"Report saved to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-path", type=str, required=True, help="Path to the input image")
    parser.add_argument("--model-path", type=str, required=True, help="Path to the .pth model file")
    parser.add_argument("--base-model", type=str, choices=["mobilenet", "efficientnet", "resnet"], required=True, help="Base model architecture used during training")
    parser.add_argument("--class-names-path", type=str, required=True, help="Path to the text file with class names (one per line)")
    parser.add_argument("--report", type=str, help="Path to save the JSON report")
    args = parser.parse_args()

    main(args.image_path, args.model_path, args.base_model, args.class_names_path, args.report)
