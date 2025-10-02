# agents/orchestrator.py
import json
from utils import EventLog
from agents.ingestion_agent import IngestionAgent
from agents.imaging_agent import ImagingAgent
from agents.therapy_agent import TherapyAgent
from agents.pharmacy_agent import PharmacyAgent
from agents.doctor_escalation_agent import DoctorEscalationAgent
import random


class Orchestrator:
    def __init__(self):
        self.event_log = EventLog()
        self.ingest = IngestionAgent(event_log=self.event_log)
        self.imaging = ImagingAgent(event_log=self.event_log)
        self.therapy = TherapyAgent(event_log=self.event_log)
        self.pharmacy = PharmacyAgent(event_log=self.event_log)
        self.doctor = DoctorEscalationAgent(event_log=self.event_log)

    def run(self, xray_path, pdf_path=None, patient_info=None, patient_lat=19.12, patient_lon=72.84):
        plan = {}
        ing = self.ingest.process_inputs(xray_path, pdf_path=pdf_path, patient_info=patient_info)
        plan['ingestion'] = ing

        img = self.imaging.predict(ing['xray_path'], patient_notes=ing.get('notes', ''))
        plan['imaging'] = img

        patient = ing['patient']
        patient['notes'] = ing.get('notes', '')

        therapy_out = self.therapy.suggest_otc(img['condition_probs'], patient)
        plan['therapy'] = therapy_out

        # Doctor Escalation Agent
        doctor_out = self.doctor.evaluate(img, therapy_out, patient)
        plan['doctor_escalation'] = doctor_out

        matches = []
        for opt in therapy_out['otc_options']:
            sku = opt['sku']
            match = self.pharmacy.find_nearest_with_stock(patient_lat, patient_lon, sku, qty=1)
            if match:
                reserved = self.pharmacy.reserve_items(match['pharmacy_id'], sku, qty=1)
                match['reserved'] = reserved
            matches.append({"sku": sku, "match": match})
        plan['pharmacy_matches'] = matches

        # Order building
        reserved_items = [m for m in matches if m['match'] and m['match'].get('reserved')]
        if reserved_items:
            order_id = f"MOCKORD-{random.randint(1000, 9999)}"
            plan['order'] = {"order_id": order_id, "items": reserved_items}
        else:
            plan['order'] = None

        plan[
            'disclaimer'] = "Educational demo only — NOT medical advice. For emergencies, call local emergency services."
        plan['event_log'] = self.event_log.to_list()
        self.event_log.log("Orchestrator", "Run completed", {"order_created": bool(plan['order'])})
        return plan