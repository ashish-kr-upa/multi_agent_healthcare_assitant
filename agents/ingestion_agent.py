# agents/ingestion_agent.py
import os
import platform
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from utils import deidentify_text

class IngestionAgent:
    def __init__(self, event_log=None):
        self.log = event_log

        # Configure tesseract path based on OS
        if platform.system() == "Windows":
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif platform.system() == "Darwin":  # macOS
            pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"
        else:  # Linux
            pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    def _extract_text_from_pdf(self, pdf_path):
        """Try extracting text from PDF, fallback to OCR if invalid."""
        text = ""
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            if self.log:
                self.log.log("IngestionAgent", f"PDF text extraction failed: {e}")
            # Try OCR on PDF as image (some PDFs are scanned images)
            try:
                text = self._ocr_image(pdf_path)
            except Exception as e2:
                if self.log:
                    self.log.log("IngestionAgent", f"OCR fallback on PDF failed: {e2}")
        return text

    def _ocr_image(self, image_path):
        """Run OCR on an image file."""
        try:
            img = Image.open(image_path)
            return pytesseract.image_to_string(img)
        except Exception as e:
            if self.log:
                self.log.log("IngestionAgent", f"OCR failed: {e}")
            return ""

    def process_inputs(self, xray_path, pdf_path=None, patient_info=None):
        """Main pipeline for ingestion of inputs (X-ray + PDF + patient notes)."""
        if not os.path.exists(xray_path):
            raise FileNotFoundError("X-ray image not found at path: " + xray_path)

        # Extract notes
        notes = ""
        if pdf_path and os.path.exists(pdf_path):
            notes = self._extract_text_from_pdf(pdf_path)

        # Fallback to OCR on X-ray if no notes
        if not notes:
            notes = self._ocr_image(xray_path)

        # De-identify PII
        notes_deid = deidentify_text(notes)

        # Patient info
        if not patient_info:
            patient = {"age": 45, "allergies": ["ibuprofen"], "notes": ""}
        else:
            patient = patient_info

        # Merge manual + extracted notes
        combined_notes = (patient.get("notes", "") + " " + notes_deid).strip()

        output = {
            "patient": patient,
            "xray_path": xray_path,
            "notes_raw": notes,
            "notes": combined_notes
        }

        if self.log:
            self.log.log("IngestionAgent", "Processed inputs", {
                "xray_path": xray_path,
                "pdf": pdf_path,
                "notes_len": len(combined_notes)
            })

        return output
