#!/usr/bin/env python3
# train.py
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import argparse
import json
import datetime
import os
import sys
import time

def round_floats(obj, precision=4):
    if isinstance(obj, float):
        return round(obj, precision)
    elif isinstance(obj, dict):
        return {k: round_floats(v, precision) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(i, precision) for i in obj]
    else:
        return obj

def get_data_loaders(data_dir, batch_size=32):
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    train_dataset = datasets.ImageFolder(root=f"{data_dir}/train", transform=train_transform)
    test_dataset = datasets.ImageFolder(root=f"{data_dir}/test", transform=test_transform)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    return train_loader, test_loader, len(train_dataset.classes)

def get_model(base_model, num_classes):
    if base_model == "mobilenet":
        model = models.mobilenet_v2(weights="IMAGENET1K_V1")
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif base_model == "efficientnet":
        model = models.efficientnet_b0(weights="IMAGENET1K_V1")
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif base_model == "resnet":
        model = models.resnet18(weights="IMAGENET1K_V1")
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    else:
        raise ValueError("Invalid base model.")
    return model

def train(model, train_loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
    accuracy = 100 * correct / total
    avg_loss = total_loss / len(train_loader)
    return avg_loss, accuracy

def evaluate(model, test_loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    accuracy = 100 * correct / total
    avg_loss = total_loss / len(test_loader)
    return avg_loss, accuracy

def generate_report(report_path, args, epochs, epoch_results, model_path, total_time):
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "arguments": vars(args),
        "epochs": epochs,
        "results": round_floats(epoch_results, 4),
        "model_save_path": model_path,
        "total_training_time": round(total_time, 4)
    }
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=4)

def print_and_log(output_file, message):
    print(message)
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "a", buffering=1) as f:
            f.write(message + "\n")

def main(data_dir, base_model, epochs, batch_size, learning_rate, model_save_path, report_path=None, output_file=None):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, test_loader, num_classes = get_data_loaders(data_dir, batch_size)
    model = get_model(base_model, num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    epoch_results = []
    total_start_time = time.time()

    for epoch in range(epochs):
        epoch_start_time = time.time()
        train_loss, train_accuracy = train(model, train_loader, criterion, optimizer, device)
        test_loss, test_accuracy = evaluate(model, test_loader, criterion, device)
        epoch_time = time.time() - epoch_start_time
        log_message = (f"Epoch [{epoch + 1}/{epochs}], "
                       f"Train Loss: {train_loss:.4f}, Train Accuracy: {train_accuracy:.2f}%, "
                       f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_accuracy:.2f}%, "
                       f"Epoch Time: {epoch_time:.2f} seconds")
        print_and_log(output_file, log_message)
        epoch_results.append(round_floats({
            "epoch": epoch + 1,
            "train_loss": train_loss,
            "train_accuracy": train_accuracy,
            "test_loss": test_loss,
            "test_accuracy": test_accuracy,
            "epoch_time_seconds": epoch_time
        }, 4))

    total_time = time.time() - total_start_time
    model_path = os.path.abspath(model_save_path)
    torch.save(model.state_dict(), model_path)
    print_and_log(output_file, f"Model saved as {model_path}")
    print_and_log(output_file, f"Total training time: {total_time:.2f} seconds")

    if report_path:
        generate_report(report_path, args, epochs, epoch_results, model_path, total_time)
        print_and_log(output_file, f"Report saved to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=str, required=True)
    parser.add_argument("--base-model", type=str, choices=["mobilenet", "efficientnet", "resnet"], required=True)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--model-save-path", type=str, required=True)
    parser.add_argument("--report", type=str)
    parser.add_argument("--output-file", type=str)
    args = parser.parse_args()
    main(args.data_dir, args.base_model, args.epochs, args.batch_size, args.learning_rate, args.model_save_path, args.report, args.output_file)
