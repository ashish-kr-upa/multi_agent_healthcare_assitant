# tests/test_agents.py
import os
import pytest
from unittest.mock import MagicMock, patch, mock_open

# Import Agent Classes
from agents.ingestion_agent import IngestionAgent
from agents.imaging_agent import ImagingAgent
from agents.therapy_agent import TherapyAgent
from agents.doctor_escalation_agent import DoctorEscalationAgent
from agents.orchestrator import Orchestrator


# --- Global Mocking Utilities ---

# Patch utils.now_ts globally to return a constant value.
@patch('utils.now_ts', return_value="2025-10-02T13:44:00")
class MockEventLog:
    def __init__(self):
        self._log = []

    def log(self, source, message, data=None):
        self._log.append({"source": source, "message": message, "data": data})

    def to_list(self):
        return self.events if hasattr(self, 'events') else self._log


# --- test_ingestion_basic ---
@patch('agents.ingestion_agent.deidentify_text', side_effect=lambda x: x)
@patch('agents.ingestion_agent.IngestionAgent._extract_text_from_pdf', return_value="PDF Notes.")
@patch('agents.ingestion_agent.IngestionAgent._ocr_image', return_value="X-Ray Text.")
@patch('os.path.exists', return_value=True)  # Mock file existence
def test_ingestion_basic(mock_exists, mock_ocr, mock_pdf, mock_deidentify, tmp_path):
    """Tests the IngestionAgent's main method and output structure."""
    xray_path = str(tmp_path / "xray.png")
    log = MockEventLog()
    ing = IngestionAgent(event_log=log)

    patient_info = {"age": 40, "allergies": ["dust"], "notes": "Patient reports cough."}

    out = ing.process_inputs(xray_path, pdf_path=None, patient_info=patient_info)

    assert "patient" in out
    assert "Processed inputs" in log._log[-1]["message"]


# --- test_imaging_output ---
@patch('agents.imaging_agent.TF_AVAILABLE', False)  # Force rule-based fallback
def test_imaging_output():
    """Tests ImagingAgent using the rule-based fallback logic."""
    log = MockEventLog()
    img = ImagingAgent(event_log=log)

    xray_path = "uploads/xray_fever.png"
    patient_notes = "Patient reports high fever."

    out = img.predict(xray_path, patient_notes=patient_notes)

    assert "condition_probs" in out
    assert out["condition_probs"]["pneumonia"] == 0.7
    assert "Predicted conditions (rule-based)" in log._log[-1]["message"]


# --- test_doctor_escalation ---
def test_doctor_escalation():
    """Tests DoctorEscalationAgent logic for a high-severity case, checking exact reason string."""
    log = MockEventLog()
    agent = DoctorEscalationAgent(event_log=log)

    imaging = {
        "condition_probs": {"pneumonia": 0.7, "normal": 0.2, "covid_suspect": 0.1},
        "severity_hint": "moderate"
    }
    therapy = {
        "otc_options": [],
        "red_flags": []
    }
    patient = {
        "notes": "chest pain and cough",
        "age": 45,
        "allergies": []
    }

    result = agent.evaluate(imaging, therapy, patient)

    expected_reasons = [
        "Imaging shows moderate pneumonia risk.",
        "Patient symptoms indicate urgent care needed.",
        "No safe OTC available for suspected pneumonia."
    ]

    assert result["recommended"] == True
    assert set(result["reasons"]) == set(expected_reasons)
    assert "Evaluated case for escalation" in log._log[-1]["message"]


# --- test_orchestrator_flow ---

# 1. Mock EventLog class
@patch('agents.orchestrator.EventLog', new=MockEventLog)
# 2. Mock Agent init/constructors to set log and mock their internal functions
# We keep these patches, as they prevent file/DB IO during init
@patch('agents.pharmacy_agent.PharmacyAgent.__init__', return_value=None)
@patch('agents.doctor_escalation_agent.DoctorEscalationAgent.__init__', return_value=None)
@patch('agents.therapy_agent.TherapyAgent.__init__', return_value=None)
@patch('agents.imaging_agent.ImagingAgent.__init__', return_value=None)
@patch('agents.ingestion_agent.IngestionAgent.__init__', return_value=None)
def test_orchestrator_flow(mock_ingest_init, mock_imaging_init, mock_therapy_init, mock_doctor_init,
                           mock_pharmacy_init):
    """Tests the Orchestrator's control flow and output structure, ensuring proper logging."""

    # --- Setup Mocks and Orchestrator ---

    log = MockEventLog()
    orch = Orchestrator()
    orch.event_log = log  # Set the log object directly

    # ----------------------------------------------------------------------
    # FIX: Define wrapper functions to ensure LOGGING happens on the mock log
    # ----------------------------------------------------------------------

    # Ingestion Agent Mock
    INGEST_OUTPUT = {
        "patient": {"notes": "cough", "age": 40, "allergies": []},
        "xray_path": "/mock/x.jpg",
        "notes": "patient reports cough and fever"
    }

    def mock_ingest_process(*args, **kwargs):
        log.log("IngestionAgent", "Processed inputs", data=INGEST_OUTPUT)
        return INGEST_OUTPUT

    orch.ingest.process_inputs = MagicMock(side_effect=mock_ingest_process)

    # Imaging Agent Mock
    IMAGING_OUTPUT = {
        "condition_probs": {"pneumonia": 0.6, "normal": 0.3, "covid_suspect": 0.1},
        "severity_hint": "moderate",
    }

    def mock_imaging_predict(*args, **kwargs):
        log.log("ImagingAgent", "Predicted conditions (DUMMY)", data=IMAGING_OUTPUT)
        return IMAGING_OUTPUT

    orch.imaging.predict = MagicMock(side_effect=mock_imaging_predict)

    # Therapy Agent Mock
    THERAPY_OUTPUT = {
        "otc_options": [{"sku": "OTC001", "drug_name": "Paracetamol"}],
        "red_flags": []
    }

    def mock_therapy_suggest(*args, **kwargs):
        log.log("TherapyAgent", "OTC suggestions computed", data=THERAPY_OUTPUT)
        return THERAPY_OUTPUT

    orch.therapy.suggest_otc = MagicMock(side_effect=mock_therapy_suggest)

    # Doctor Escalation Agent Mock
    DOCTOR_OUTPUT = {
        "recommended": False, "reasons": [], "doctor": None,
    }

    def mock_doctor_evaluate(*args, **kwargs):
        log.log("DoctorEscalationAgent", "Evaluated case for escalation", data=DOCTOR_OUTPUT)
        return DOCTOR_OUTPUT

    orch.doctor.evaluate = MagicMock(side_effect=mock_doctor_evaluate)

    # Pharmacy Agent Mocks
    PHARMACY_MATCH = {"pharmacy_id": "P1", "distance_km": 5.0}

    def mock_pharmacy_find(*args, **kwargs):
        log.log("PharmacyAgent", "Matched pharmacy", data=PHARMACY_MATCH)
        return PHARMACY_MATCH

    def mock_pharmacy_reserve(*args, **kwargs):
        log.log("PharmacyAgent", f"Reserved 1 of {args[1]} at {args[0]}")
        return True

    orch.pharmacy.find_nearest_with_stock = MagicMock(side_effect=mock_pharmacy_find)
    orch.pharmacy.reserve_items = MagicMock(side_effect=mock_pharmacy_reserve)

    # --- Run Test ---
    plan = orch.run("/mock/x.jpg", pdf_path="/mock/report.pdf")

    # --- Assertions ---
    # Assert all agent methods in the pipeline were called exactly once
    orch.ingest.process_inputs.assert_called_once()
    orch.imaging.predict.assert_called_once()
    orch.therapy.suggest_otc.assert_called_once()
    orch.doctor.evaluate.assert_called_once()
    orch.pharmacy.find_nearest_with_stock.assert_called_once()
    orch.pharmacy.reserve_items.assert_called_once()

    # Check that the log was populated
    # Expected logs: Ingestion (1), Imaging (1), Therapy (1), Doctor (1), Pharmacy Find (1), Pharmacy Reserve (1), Orchestrator Final (1) = 7 entries
    assert len(plan["event_log"]) >= 7
    assert "Run completed" in plan["event_log"][-1]["message"]