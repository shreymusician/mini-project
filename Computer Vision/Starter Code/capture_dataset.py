"""capture_dataset.py - grab labelled photos from the ESP32-CAM and log metadata.
Usage: python capture_dataset.py http://<camera-ip>
Type the plant id and label once, then press Enter to take each photo. Type q to quit."""
import csv, os, sys, time
from datetime import datetime
import requests

CAM = sys.argv[1].rstrip("/")
OUT = "dataset_raw"
META = os.path.join(OUT, "metadata.csv")
os.makedirs(OUT, exist_ok=True)
new = not os.path.exists(META)
f = open(META, "a", newline="", encoding="utf-8")
w = csv.writer(f)
if new:
    w.writerow(["file", "plant_id", "label", "crop", "date", "time", "weather", "light", "distance_cm", "angle", "source", "notes"])

plant = input("plant_id (e.g. T-014): ").strip()
label = input("label (healthy / early_blight / late_blight / ...): ").strip()
weather = input("weather (sunny/cloudy/shade): ").strip()
dist = input("camera distance in cm: ").strip()
n = 0
while True:
    cmd = input("Enter = shoot, q = quit, a = angle note: ").strip().lower()
    if cmd == "q":
        break
    angle = "front"
    if cmd == "a":
        angle = input("angle (front/left/right/top/underside): ").strip()
    r = requests.get(CAM + "/capture", timeout=10)
    now = datetime.now()
    name = "%s_%s_%03d.jpg" % (plant, now.strftime("%Y%m%d_%H%M%S"), n)
    os.makedirs(os.path.join(OUT, label), exist_ok=True)
    with open(os.path.join(OUT, label, name), "wb") as g:
        g.write(r.content)
    w.writerow([name, plant, label, "tomato", now.date(), now.strftime("%H:%M:%S"), weather, "", dist, angle, "esp32cam", ""])
    f.flush()
    n += 1
    print("saved", name, "(%d bytes)" % len(r.content))
f.close()
