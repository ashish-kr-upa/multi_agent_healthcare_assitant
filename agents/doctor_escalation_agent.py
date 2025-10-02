# agents/doctor_escalation_agent.py
from utils import now_ts

class DoctorEscalationAgent:
    def __init__(self, event_log=None):
        self.log = event_log

    def evaluate(self, imaging, therapy, patient):
        """
        Decide whether to escalate case to a doctor.
        """

        escalation_reasons = []

        # Imaging-based rules
        probs = imaging.get("condition_probs", {})
        severity = imaging.get("severity_hint", "mild")

        if severity in ["moderate", "severe"]:
            escalation_reasons.append(f"Imaging shows {severity} pneumonia risk.")

        if probs.get("covid_suspect", 0) > 0.5:
            escalation_reasons.append("High probability of COVID suspect.")

        # Therapy-based rules
        if therapy.get("red_flags"):
            escalation_reasons.extend(therapy["red_flags"])

        # Patient-based rules
        notes = (patient.get("notes") or "").lower()
        if "chest pain" in notes or "shortness of breath" in notes:
            escalation_reasons.append("Patient symptoms indicate urgent care needed.")

        # If no OTC available for pneumonia/covid
        if not therapy.get("otc_options") and probs.get("pneumonia", 0) > 0.6:
            escalation_reasons.append("No safe OTC available for suspected pneumonia.")

        recommended = len(escalation_reasons) > 0

        # If escalation is recommended, assign a doctor
        doctor_info = None
        if recommended:
            # Simple mock roster pick
            doctor_info = {
                "doctor_id": "doc001" if "pneumonia" in escalation_reasons[0] else "doc002",
                "name": "Dr. A Chopra" if "pneumonia" in escalation_reasons[0] else "Dr. S Patel",
                "tele_slot": "2025-10-01T09:00:00"
            }

        output = {
            "recommended": recommended,
            "reasons": escalation_reasons,
            "doctor": doctor_info,
            "meta": {"ts": now_ts()}
        }

        if self.log:
            self.log.log("DoctorEscalationAgent", "Evaluated case for escalation", output)
        return output