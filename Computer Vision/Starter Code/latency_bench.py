"""latency_bench.py - measure (a) ESP32-CAM snapshot time and (b) model inference time.
Usage: python latency_bench.py http://<camera-ip> classifier_seed0.keras"""
import statistics, sys, time
import numpy as np, requests, tensorflow as tf

def stats(v):
    v = sorted(v)
    return {"n": len(v), "median_ms": statistics.median(v), "p95_ms": v[int(0.95 * len(v)) - 1], "mean_ms": statistics.mean(v)}

cam = []
for _ in range(100):
    t = time.perf_counter()
    r = requests.get(sys.argv[1].rstrip("/") + "/capture", timeout=10)
    cam.append((time.perf_counter() - t) * 1000)
print("camera snapshot", stats(cam), "last size", len(r.content))

model = tf.keras.models.load_model(sys.argv[2])
x = np.random.rand(1, 224, 224, 3).astype("float32") * 255
model.predict(x, verbose=0)  # warm-up
inf = []
for _ in range(100):
    t = time.perf_counter()
    model.predict(x, verbose=0)
    inf.append((time.perf_counter() - t) * 1000)
print("classifier inference (this laptop/Colab CPU or GPU - say which!)", stats(inf))
