# agents/imaging_agent.py
import numpy as np
import os
from utils import now_ts

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing import image

    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class ImagingAgent:
    def __init__(self, event_log=None, model_path="models/imaging_cnn.h5"):
        self.log = event_log
        self.model = None
        self.class_labels = ["normal", "pneumonia", "covid_suspect"]

        if TF_AVAILABLE and os.path.exists(model_path):
            try:
                self.model = load_model(model_path)
                if self.log:
                    self.log.log("ImagingAgent", "Loaded CNN model successfully")
            except Exception as e:
                if self.log:
                    self.log.log("ImagingAgent", f"Failed to load CNN model: {e}")
        else:
            if self.log:
                self.log.log("ImagingAgent", "CNN model not available, using rule-based fallback")

    def predict(self, xray_path, patient_notes=""):
        # If model is available, use it
        if self.model is not None:
            return self._predict_with_cnn(xray_path)
        else:
            return self._predict_with_rules(xray_path, patient_notes)

    def _predict_with_cnn(self, xray_path):
        # Preprocess image
        img = image.load_img(xray_path, target_size=(64, 64))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        preds = self.model.predict(img_array)[0]
        probs = {cls: float(round(preds[i], 2)) for i, cls in enumerate(self.class_labels)}

        # Severity heuristic (just a rule on pneumonia prob)
        severity = "mild"
        if probs["pneumonia"] > 0.5:
            severity = "moderate"
        if probs["pneumonia"] > 0.75:
            severity = "severe"

        output = {
            "condition_probs": probs,
            "severity_hint": severity,
            "meta": {"ts": now_ts(), "file": os.path.basename(xray_path), "model": "CNN"}
        }

        if self.log:
            self.log.log("ImagingAgent", "Predicted conditions (CNN)", output)
        return output

    def _predict_with_rules(self, xray_path, patient_notes=""):
        """
        Rule-based stub classifier.
        Conditions are influenced by keywords in notes or filename.
        """
        fname = os.path.basename(xray_path).lower()
        notes = (patient_notes or "").lower()

        probs = {"pneumonia": 0.2, "normal": 0.6, "covid_suspect": 0.2}

        if "pneumonia" in fname or "fever" in notes or "cough" in notes:
            probs = {"pneumonia": 0.7, "normal": 0.2, "covid_suspect": 0.1}
        elif "covid" in fname or "breath" in notes:
            probs = {"pneumonia": 0.2, "normal": 0.2, "covid_suspect": 0.6}
        elif "normal" in fname or "checkup" in notes:
            probs = {"pneumonia": 0.1, "normal": 0.8, "covid_suspect": 0.1}

        # Decide severity
        severity = "mild"
        if probs["pneumonia"] > 0.5:
            severity = "moderate"
        if probs["pneumonia"] > 0.75:
            severity = "severe"

        output = {
            "condition_probs": probs,
            "severity_hint": severity,
            "meta": {"ts": now_ts(), "file": fname, "model": "rule-based"}
        }

        if self.log:
            self.log.log("ImagingAgent", "Predicted conditions (rule-based)", output)
        return output