"""make_splits.py - split by PLANT (never by image) into train/val/test.
Reads dataset_raw/metadata.csv, writes dataset_split/{train,val,test}/<label>/*.jpg"""
import csv, os, random, shutil
from collections import defaultdict

random.seed(42)
RAW, OUT = "dataset_raw", "dataset_split"
rows = list(csv.DictReader(open(os.path.join(RAW, "metadata.csv"), encoding="utf-8")))
plants = defaultdict(list)
for r in rows:
    plants[(r["label"], r["plant_id"])].append(r)

by_label = defaultdict(list)
for (label, pid) in plants:
    by_label[label].append(pid)

assign = {}
for label, pids in by_label.items():
    random.shuffle(pids)
    n = len(pids)
    n_test = max(1, round(0.15 * n)) if n >= 3 else 0
    n_val = max(1, round(0.15 * n)) if n >= 3 else 0
    for i, pid in enumerate(pids):
        assign[(label, pid)] = "test" if i < n_test else "val" if i < n_test + n_val else "train"
    print(label, "plants:", n, "-> test", n_test, "val", n_val)

for (label, pid), items in plants.items():
    s = assign[(label, pid)]
    os.makedirs(os.path.join(OUT, s, label), exist_ok=True)
    for r in items:
        shutil.copy(os.path.join(RAW, label, r["file"]), os.path.join(OUT, s, label, r["file"]))
print("done. Check that no plant_id appears in more than one split.")
