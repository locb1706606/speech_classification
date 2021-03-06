import os
import numpy as np
import joblib
from keras.models import load_model


prediction_filename = "submission.csv"
try:
    os.remove(prediction_filename)
except Exception:
    pass

model = load_model("model.h5")
test_data = joblib.load("tmp/test.data.bin")

map_values = [(0, 1), (0, 0), (0, 2), (1, 1), (1, 0), (1, 2)]
prediction_file = open(prediction_filename, "a")
prediction_file.write("id,gender,accent\n")
count_error_file = 0
for label, X in test_data:
    try:
        value = np.bincount(np.argmax(model.predict(X), axis=1)).argmax()
    except:
        print(f"Cannot detect file {label}")
        value = 0
        count_error_file += 1
    gender, accent = map_values[value]
    prediction_file.write(f"{label},{gender},{accent}\n")
print(f"Results is saved in file {prediction_filename}")