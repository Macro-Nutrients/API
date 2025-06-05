from flask import Blueprint, request, jsonify, current_app
import numpy as np
import io
from PIL import Image
import uuid
from tensorflow.keras.preprocessing.image import img_to_array
from google.cloud import firestore
from services.store_data import store_data

inference_bp = Blueprint('inference', __name__)

CLASS_NAMES = ["ayam_goreng", "burger", "donat", "kentang_goreng", "mie_goreng"]

def preprocess_image(image_bytes, target_size=(224, 224)):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(target_size)
    arr = img_to_array(img).astype("float32") / 255.0
    return np.expand_dims(arr, axis=0)

@inference_bp.route('/predict', methods=['POST'])
def predict():
    keras_model = current_app.config.get('KERAS_MODEL')
    if keras_model is None:
        return jsonify(error=True, message="Model belum tersedia"), 500

    if 'image' not in request.files:
        return jsonify(error=True, message="Key 'image' tidak ditemukan"), 400

    file = request.files['image']
    if file.filename == "":
        return jsonify(error=True, message="Nama file kosong"), 400

    try:
        x = preprocess_image(file.read())
        preds = keras_model.predict(x)
        idx = int(np.argmax(preds[0]))
        label = CLASS_NAMES[idx]
        confidence = float(preds[0][idx])

        doc_id = uuid.uuid4().hex
        store_data("predictions", doc_id, {
            "label": label,
            "confidence": confidence,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        return jsonify(error=False, result={"label": label, "confidence": confidence}), 200
    except Exception as e:
        current_app.logger.error(f"[PREDICT ERROR] {e}")
        return jsonify(error=True, message="Gagal melakukan prediksi"), 500

@inference_bp.route('/labels', methods=['GET'])
def get_labels():
    return jsonify(error=False, labels=CLASS_NAMES), 200
