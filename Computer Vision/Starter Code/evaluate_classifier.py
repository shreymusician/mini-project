"""evaluate_classifier.py - evaluate a saved model on ANY test folder (cross-domain test).
Usage: python evaluate_classifier.py classifier_seed0.keras path/to/test_dir classes.json out.json
classes.json = list of class names in the SAME order as training (see classifier_seed0.json 'classes')."""
import json, sys
import numpy as np, tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, f1_score

model = tf.keras.models.load_model(sys.argv[1])
names = json.load(open(sys.argv[3]))
ds = tf.keras.utils.image_dataset_from_directory(sys.argv[2], image_size=(224, 224), batch_size=32, shuffle=False,
                                                class_names=names)
y_true = np.concatenate([y.numpy() for _, y in ds])
y_pred = model.predict(ds).argmax(1)
res = {"n_images": int(len(y_true)), "acc": float((y_true == y_pred).mean()),
       "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
       "confusion": confusion_matrix(y_true, y_pred, labels=range(len(names))).tolist()}
json.dump(res, open(sys.argv[4], "w"), indent=1)
print(res["acc"], res["macro_f1"])
