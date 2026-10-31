"""train_detector.py - single-class plant detector with Ultralytics YOLOv8n (Colab GPU).
pip install ultralytics
plant.yaml example:
  path: /content/plant_det
  train: images/train
  val: images/val
  test: images/test
  names: {0: plant}
Include NEGATIVE images (people, soil, pots, buildings) with EMPTY label .txt files."""
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.train(data="plant.yaml", epochs=80, imgsz=640, batch=16, seed=0, project="runs", name="plant_v1")
m = model.val(data="plant.yaml", split="test")
print("precision", m.box.mp, "recall", m.box.mr, "mAP50", m.box.map50, "mAP50-95", m.box.map)
model.export(format="tflite", imgsz=640)   # for the dashboard / edge runtime
