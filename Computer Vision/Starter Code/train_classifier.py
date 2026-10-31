"""train_classifier.py - MobileNetV3-Small leaf-health classifier (TensorFlow/Keras).
Run on Colab GPU. Folder layout: dataset_split/{train,val,test}/<class>/*.jpg
Usage: python train_classifier.py <seed>"""
import json, sys, time
import numpy as np, tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, f1_score

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 0
tf.keras.utils.set_random_seed(SEED)
IMG = (224, 224)
BS = 32
D = "dataset_split"
train = tf.keras.utils.image_dataset_from_directory(D + "/train", image_size=IMG, batch_size=BS, seed=SEED)
val = tf.keras.utils.image_dataset_from_directory(D + "/val", image_size=IMG, batch_size=BS, shuffle=False)
test = tf.keras.utils.image_dataset_from_directory(D + "/test", image_size=IMG, batch_size=BS, shuffle=False)
names = train.class_names
aug = tf.keras.Sequential([tf.keras.layers.RandomFlip("horizontal_and_vertical"), tf.keras.layers.RandomRotation(0.1),
                           tf.keras.layers.RandomZoom(0.15), tf.keras.layers.RandomBrightness(0.2),
                           tf.keras.layers.RandomContrast(0.2)])
base = tf.keras.applications.MobileNetV3Small(input_shape=IMG + (3,), include_top=False, weights="imagenet")
base.trainable = False
inp = tf.keras.Input(IMG + (3,))
x = aug(inp)
x = base(x, training=False)   # MobileNetV3 in Keras rescales 0-255 inputs internally
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.3)(x)
out = tf.keras.layers.Dense(len(names), activation="softmax")(x)
model = tf.keras.Model(inp, out)
model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
h1 = model.fit(train, validation_data=val, epochs=8)
base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False
model.compile(optimizer=tf.keras.optimizers.Adam(1e-4), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
h2 = model.fit(train, validation_data=val, epochs=12,
               callbacks=[tf.keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True)])

y_true = np.concatenate([y.numpy() for _, y in test])
y_prob = model.predict(test)
y_pred = y_prob.argmax(1)
res = {"seed": SEED, "classes": names, "test_acc": float((y_true == y_pred).mean()),
       "macro_f1": float(f1_score(y_true, y_pred, average="macro")),
       "confusion": confusion_matrix(y_true, y_pred).tolist(),
       "report": classification_report(y_true, y_pred, target_names=names, output_dict=True)}
json.dump(res, open("classifier_seed%d.json" % SEED, "w"), indent=1)
model.save("classifier_seed%d.keras" % SEED)
print("acc %.4f  macroF1 %.4f" % (res["test_acc"], res["macro_f1"]))
