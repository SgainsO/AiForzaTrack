from ultralytics import YOLO
import torch
# Load a model
model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

# Use the model
if __name__ == '__main__':    
    model.train(data="C:\\Users\\sudar\\Downloads\\cones\\data.yaml", epochs=180)  # train the model
    metrics = model.val()  # evaluate model performance on the validation set
    path = model.export(format="onnx")  # export the model to ONNX format

