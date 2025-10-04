# app.py

import streamlit as st
import os
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# *** CRITICAL: Import classes by their original names ***
from agents.orchestrator import Orchestrator
from utils_display import (
    colorize_json,
    display_metric_card,
    display_agent_card,
    display_medication_card,
    display_pharmacy_card,
)

#uploads directory
os.makedirs("uploads", exist_ok=True)

# Custom CSS for theme application
st.markdown("""
<style>
    /* --- GLOBAL LAYOUT & COLOR SCHEME --- */
    .stApp { 
        background-color: #f0bb0e; /* Light Gray Main Background */
    }
    .main {
        background-color: #f0bb0e;
    }

    /* Sidebar styling for brand distinction */
    [data-testid="stSidebar"] {
        background-color: #000080; /* Navy Blue */
        color: #ffffff; /* Default text color for contrast */
    }

    /* Ensure input labels are visible on the dark sidebar */
    label {
        color: #ffffff;
    }

    /* Global styles */
    .main-header {
        text-align: center;
        color: #2c5282;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 2.5rem;
    }

    /* Disclaimer without box */
    .disclaimer {
        color: #4a5568;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        padding: 0.5rem 0;
        text-align: center;
    }

    .disclaimer strong {
        color: #e53e3e;
    }

    /* Card styles with dark blue text */
    .card {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }

    .card-title {
        color: #2c5282;
        font-size: 1.25rem;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 1rem;
    }

    .card-text {
        color: #2c5282;
        line-height: 1.6;
    }

    .card-highlight {
        color: #2b6cb0;
        font-weight: 600;
    }

    /* Metric cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid #e2e8f0;
        border-top: 4px solid #4299e1;
        height: 100%;
        transition: all 0.3s ease;
        overflow: hidden;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
    }

    .metric-title {
        color: #2c5282;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }

    .metric-value {
        color: #2b6cb0;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
        hyphens: auto;
    }

    .metric-subtitle {
        color: #4a5568;
        font-size: 0.8rem;
        margin: 0;
        line-height: 1.2;
    }

    /* Status-specific card styles */
    .card-mild {
        background-color: #f0fff4;
        border-left: 5px solid #48bb78;
    }

    .card-moderate {
        background-color: #fffbf0;
        border-left: 5px solid #ed8936;
    }

    .card-severe {
        background-color: #fff5f5;
        border-left: 5px solid #f56565;
    }

    .card-escalation-yes {
        background-color: #fff5f5;
        border-left: 5px solid #f56565;
    }

    .card-escalation-no {
        background-color: #f0fff4;
        border-left: 5px solid #48bb78;
    }

    /* Medication cards */
    .medication-card {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #4299e1;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .medication-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.08);
    }

    .medication-title {
        color: #2c5282;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 0.75rem;
    }

    .medication-detail {
        color: #2c5282;
        margin: 0.25rem 0;
    }

    .medication-warning {
        background-color: #fef5e7;
        color: #744210;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-block;
        margin-top: 0.5rem;
    }

    /* Pharmacy cards */
    .pharmacy-card {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #38b2ac;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .pharmacy-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.08);
    }

    .pharmacy-title {
        color: #2c5282;
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 0.75rem;
    }

    .pharmacy-detail {
        color: #2c5282;
        margin: 0.25rem 0;
    }

    .pharmacy-status {
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        display: inline-block;
        margin-top: 0.5rem;
    }

    .status-reserved {
        background-color: #c6f6d5;
        color: #22543d;
    }

    .status-available {
        background-color: #feebc8;
        color: #7c2d12;
    }

    /* Event log with visible text */
    .event-log-item {
        background-color: #f8fafc;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
        border-left: 3px solid #4299e1;
        font-family: monospace;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .event-timestamp {
        color: #4a5568;
        font-weight: 600;
    }

    .event-source {
        color: #2b6cb0;
        font-style: italic;
        font-weight: 600;
    }

    .event-message {
        color: #2d3748;
        margin-top: 0.25rem;
    }

    /* Expander styling for event log */
    .event-expander {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .event-expander-header {
        background-color: #edf2f7;
        border: 1px solid #cbd5e0;
        border-radius: 0.375rem;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .event-expander-header:hover {
        background-color: #e2e8f0;
    }

    .event-expander-content {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 0.375rem;
        padding: 1rem;
        margin-top: 0.25rem;
    }

    .event-expander-title {
        color: #2c5282;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 0;
        margin-bottom: 0.5rem;
    }

    /* Analytics specific styles */
    .analytics-card {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        min-height: 200px;
        display: flex;
        flex-direction: column;
    }

    .analytics-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
    }

    .analytics-title {
        color: #2c5282;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-shrink: 0;
    }

    .analytics-icon {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }

    .analytics-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 0;
    }

    .analytics-value {
        color: #2b6cb0;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
        hyphens: auto;
        line-height: 1.2;
    }

    .analytics-subtitle {
        color: #4a5568;
        font-size: 0.85rem;
        margin: 0.25rem 0 0 0;
        line-height: 1.2;
    }

    .severity-indicator {
        width: 100%;
        height: 8px;
        border-radius: 4px;
        margin: 0.5rem 0;
        background: linear-gradient(90deg, #48bb78 0%, #ed8936 50%, #f56565 100%);
        position: relative;
    }

    .severity-marker {
        position: absolute;
        top: -4px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    .confidence-meter {
        width: 100%;
        height: 20px;
        background-color: #e2e8f0;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }

    .confidence-fill {
        height: 100%;
        background: linear-gradient(90deg, #4299e1, #2b6cb0);
        border-radius: 10px;
        transition: width 1s ease;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 0.5rem;
    }

    .confidence-text {
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
    }

    .insight-box {
        background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
        border-left: 4px solid #4299e1;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }

    .insight-title {
        color: #2c5282;
        font-weight: 600;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    .insight-text {
        color: #2d3748;
        font-size: 0.85rem;
        margin: 0;
        line-height: 1.4;
    }

    /* --- TABS STYLING --- */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        border-bottom: 2px solid #e2e8f0;
        border-radius: 0;
        padding: 0;
        margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        color: #092c47; /* <-- NEW TEXT COLOR FOR TABS */
        font-weight: 500;
        padding: 0.75rem 1rem;
        border-radius: 0;
        border-bottom: 2px solid transparent;
        transition: all 0.3s ease;
        background-color: transparent;
        margin-right: 0.5rem;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #2c5282;
        border-bottom-color: #4299e1;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #2c5282;
        border-bottom-color: #4299e1;
        background-color: transparent;
        font-weight: 600;
    }

    /* Sidebar specific styling 
    .sidebar-header {
        background-color: #000080; 
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    .sidebar-header h3 {
        color: #ffffff; /* White text for contrast */
        margin-top: 0;
    }

    .sidebar-section h4 {
        color: #c0c0c0; /* Light grey text */
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #4a5568;
        margin-top: 2rem;
        padding: 1rem;
        background-color: #f7fafc;
        border-radius: 0.5rem;
    }

    /* Download button */
    .download-button {
        background-color: #4299e1;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-weight: 500;
        cursor: pointer;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }

    .download-button:hover {
        background-color: #3182ce;
        transform: translateY(-1px);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #4c7cad;
        border-radius: 0.5rem;
        border: 1px solid #e2e8f0;
    }

    .streamlit-expanderHeader:hover {
        background-color: #edf2f7;
    }
</style>
""", unsafe_allow_html=True)

# Title and disclaimer (no box)
st.markdown('<h1 class="main-header">🏥 Multi-Agent Healthcare Triage System</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Regulatory Disclaimer:</strong> This is an <strong>Educational Prototype</strong>.  
    It <strong>MUST NOT</strong> be used for actual diagnosis or patient care.
</div>
""", unsafe_allow_html=True)

# Sidebar inputs - Data Acquisition Prompts
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h3>🗄️ Patient Data Acquisition</h3></div>', unsafe_allow_html=True)

    uploaded_xray = st.file_uploader("📷 Required: Chest X-ray (PNG/JPG)", type=["png", "jpg", "jpeg"])
    uploaded_pdf = st.file_uploader("📄 Optional: Clinical Report / ID (PDF)", type=["pdf"])

    st.markdown('<div class="sidebar-section"><h4>🧑 Patient Context</h4></div>', unsafe_allow_html=True)
    age = st.number_input("Patient Age", min_value=0, max_value=120, value=45)
    allergies_input = st.text_input("Known Allergies (e.g., ibuprofen, penicillin)", value="ibuprofen")

    st.markdown('<div class="sidebar-section"><h4>📝 Symptom Summary</h4></div>', unsafe_allow_html=True)
    notes_input = st.text_area(
        "Enter symptoms & brief history (Manual Input)",
        placeholder="Example: persistent cough, mild fever for 3 days, no breathing difficulty.",
        height=100
    )

    st.markdown('<div class="sidebar-section"><h4>📍 Fulfillment Location</h4></div>', unsafe_allow_html=True)
    patient_lat = st.number_input("Latitude (Delivery Point)", value=19.12, format="%.6f")
    patient_lon = st.number_input("Longitude (Delivery Point)", value=72.84, format="%.6f")

    run_button = st.button("🚀 EXECUTE MULTI-AGENT PIPELINE", use_container_width=True)

# Main execution
if run_button:
    if not uploaded_xray:
        st.error("🚨 X-ray image is required to initiate the Ingestion Agent.")
    else:
        # 1. Prepare Inputs for Orchestrator
        xray_path = os.path.join("uploads", uploaded_xray.name)
        with open(xray_path, "wb") as f:
            f.write(uploaded_xray.read())

        pdf_path = None
        if uploaded_pdf:
            pdf_path = os.path.join("uploads", uploaded_pdf.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.read())

        patient_payload = {  # Using 'payload' for the input dict for better separation
            "age": int(age),
            "allergies": [a.strip() for a in allergies_input.split(",") if a.strip()],
            "notes": notes_input
        }

        # 2. Call the Orchestrator
        orch = Orchestrator()
        with st.spinner("Processing data through sequential AI agents (Ingestion -> Imaging -> Therapy)..."):
            # CRITICAL: Call the original run() method with the specific arguments
            plan = orch.run(
                xray_path,
                pdf_path=pdf_path,
                patient_info=patient_payload,
                patient_lat=patient_lat,
                patient_lon=patient_lon
            )

        # --- Summary Cards ---
        st.markdown("## 📊 Final Triage and Fulfillment Summary")

        # Pull key data points for the metric cards
        condition_probs = plan["imaging"]["condition_probs"]
        top_condition = max(condition_probs, key=condition_probs.get)
        top_prob = condition_probs[top_condition]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            display_metric_card("Primary Diagnosis", top_condition.title(), f"Confidence: {top_prob:.0%}",
                                color="#2b6cb0")
        with col2:
            esc = plan["doctor_escalation"]["recommended"]
            reasons = plan["doctor_escalation"].get("reasons", [])
            reason_text = reasons[0] if reasons else "No mandatory referral"
            display_metric_card("Mandatory Referral", "YES" if esc else "NO", reason_text,
                                color="#f56565" if esc else "#48bb78")
        with col3:
            order = plan["order"]
            display_metric_card("Fulfillment Status", "ORDER CREATED" if order else "NO ORDER",
                                order["order_id"] if order else "No safe items suggested",
                                color="#48bb78" if order else "#718096")
        with col4:
            otc_count = len(plan["therapy"]["otc_options"])
            display_metric_card("OTC Options", str(otc_count), "Meds passed safety check", color="#ed8936")

        # --- Detailed Tabs ---
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            ["📥 Ingestion", "📝 Clean Notes", "🩻 Diagnostics", "💊 Therapy Plan", "👨‍⚕️ Referral", "🏪 Fulfillment",
             "📜 Audit Log"]
        )

        with tab1:
            st.markdown("### 📥 Ingestion Agent: Data Transformation")
            patient = plan["ingestion"]["patient"]

            # Displaying Agent outputs using humanized titles
            display_agent_card("Patient Context Payload",
                               f"<p class='card-text'><span class='card-highlight'>Age:</span> {patient['age']}</p><p class='card-text'><span class='card-highlight'>Allergies:</span> {', '.join(patient['allergies']) or 'None Reported'}</p>")

            display_agent_card("Source File Integrity Check",
                               f"<p class='card-text'><span class='card-highlight'>X-ray Path:</span> {os.path.basename(plan['ingestion']['xray_path'])}</p><p class='card-text'><span class='card-highlight'>PDF Status:</span> {'Extracted' if pdf_path else 'No PDF Provided'}</p>")

            display_agent_card("Data Processing Summary",
                               f"<p class='card-text'><span class='card-highlight'>Text Extracted (OCR/PDF):</span> {'Yes' if plan['ingestion']['notes_raw'] else 'No'}</p><p class='card-text'><span class='card-highlight'>PII Masking Applied:</span> {'Yes (De-ID)' if plan['ingestion']['notes'] != plan['ingestion']['notes_raw'] else 'No changes needed'}</p>")

        with tab2:
            st.markdown("### 📝 Combined and Sanitized Notes")
            if plan["ingestion"].get("notes"):
                display_agent_card("Notes Used for Downstream Agents (Masked)",
                                   f"<p class='card-text'>{plan['ingestion']['notes']}</p>")
                if plan["ingestion"]["notes_raw"]:
                    with st.expander("View RAW Extracted Text (Pre-Masking)"):
                        st.code(plan["ingestion"]["notes_raw"])
            else:
                st.info("No text notes were provided or extracted via OCR.")

        with tab3:
            st.markdown("### 🩻 Imaging Agent: Model Inference Results")

            probs = plan["imaging"]["condition_probs"]
            severity = plan["imaging"]["severity_hint"]
            model_info = plan["imaging"]["meta"]

            # --- Analytics: Metrics Row ---
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                display_metric_card("Model Used", model_info.get("model_name", "N/A"),
                                    f"Version: {model_info.get('version', 'N/A')}", color="#4299e1")
            with col_a2:
                display_metric_card("Highest Severity", severity.upper(), "Based on clinical scoring", color="#ed8936")
            with col_a3:
                display_metric_card("Run Time", f"{plan['imaging'].get('runtime_ms', 'N/A')} ms",
                                    "Model inference time", color="#48bb78")

            # --- Analytics: Charts Row ---
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📊 Condition Probability Distribution")
                # Create bar chart
                fig_bar = px.bar(
                    x=list(probs.keys()), y=list(probs.values()),
                    labels={"x": "Condition", "y": "Probability"},
                    color=list(probs.values()), color_continuous_scale=["#bee3f8", "#2b6cb0"],
                    title="Model Confidence by Condition"
                )
                fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#2c5282",
                                      height=300)
                st.plotly_chart(fig_bar, use_container_width=True)

            with col2:
                st.markdown("#### 🥧 Probability Breakdown")
                # Create pie chart
                fig_pie = px.pie(
                    values=list(probs.values()), names=list(probs.keys()), title="Condition Distribution",
                    color_discrete_map={"normal": "#48bb78", "pneumonia": "#ed8936", "covid_suspect": "#f56565"}
                )
                fig_pie.update_layout(font_color="#2c5282", height=300, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)

            # --- Detailed Analysis ---
            st.markdown("#### 🔬 Model Insight")
            st.markdown(f"""
            <div class="insight-box">
                <p class="insight-title">Highest Risk Identified</p>
                <p class="insight-text">The model predicts **{top_condition.title()}** with a confidence of **{top_prob:.2%}**. The clinical severity hint is **{severity.upper()}**.</p>
            </div>
            """, unsafe_allow_html=True)

        with tab4:
            st.markdown("### 💊 Therapy Agent: OTC Treatment Plan")
            if plan["therapy"]["red_flags"]:
                for flag in plan["therapy"]["red_flags"]:
                    display_agent_card("⚠️ **Safety/Contraindication Alert**", f"<p class='card-text'>{flag}</p>",
                                       card_type="severe")

            if plan["therapy"]["otc_options"]:
                st.markdown("#### Safe Medication Suggestions:")
                for med in plan["therapy"]["otc_options"]:
                    st.markdown(display_medication_card(med), unsafe_allow_html=True)
            else:
                st.info("No safe OTC medications were suggested, likely due to red flags or missing data.")

        with tab5:
            st.markdown("### 👨‍⚕️ Doctor Escalation Agent: Final Risk Review")
            esc = plan["doctor_escalation"]
            if esc["recommended"]:
                reasons = "".join([f"<li>{r}</li>" for r in esc.get("reasons", [])])
                display_agent_card("🔴 **Mandatory Referral Required**",
                                   f"**Reasons for Escalation:** <ul class='card-text'>{reasons}</ul>",
                                   card_type="escalation-yes")
                if esc.get("doctor"):
                    doc = esc["doctor"]
                    display_agent_card("Assigned Tele-Consult Slot",
                                       f"<p class='card-text'><span class='card-highlight'>Dr.</span> {doc['name']} (ID: {doc['doctor_id']})<br><span class='card-highlight'>Confirmed Slot:</span> {doc['tele_slot']}</p>")
            else:
                display_agent_card("🟢 **Escalation NOT Required**",
                                   "<p class='card-text'>Risk assessment indicates low acuity. Proceeding to fulfillment.</p>",
                                   card_type="escalation-no")

        with tab6:
            st.markdown("### 🏪 Pharmacy Agent: Fulfillment & Logistics")
            st.markdown("#### 📍 Nearest Pharmacies with Stock Check:")
            for match_data in plan["pharmacy_matches"]:
                match = match_data["match"]
                sku = match_data["sku"]
                if match and match.get("pharmacy_id"):
                    st.markdown(display_pharmacy_card(match, reserved=match.get("reserved", False)),
                                unsafe_allow_html=True)
                else:
                    display_agent_card("SKU Stock Alert",
                                       f"<p class='card-text'>SKU **{sku}**: No nearby pharmacy found with available stock.</p>",
                                       card_type="moderate")

            if plan["order"]:
                order = plan["order"]
                st.markdown("#### Final Order Confirmation:")
                display_agent_card("Order Details",
                                   f"<p class='card-text'><span class='card-highlight'>Order ID:</span> {order['order_id']}</p><p class='card-text'><span class='card-highlight'>Items Reserved:</span> {len(order['items'])}</p>")
                st.download_button("⬇️ Download Fulfillment JSON", data=json.dumps(order, indent=2),
                                   file_name=f"order_{order['order_id']}.json", mime="application/json")
            else:
                st.info("Fulfillment was halted: No safe or available items were reserved.")

        with tab7:
            st.markdown("### 📜 System Audit Log (Chronological)")
            # Event log with improved visibility
            for event in plan["event_log"][::-1][:20]:
                st.markdown(f"""
                <div class="event-log-item">
                    <span class="event-timestamp">{event['ts']}</span> - 
                    <span class="event-source">[{event['source']}]</span>: 
                    <span class="event-message">{event['message']}</span>
                </div>
                """, unsafe_allow_html=True)

                if event.get("data"):
                    expander_title = f"📋 View raw data from [{event['source']}]"
                    with st.expander(expander_title, expanded=False):
                        st.markdown(f"""
                        <div class="event-expander" style="margin-top: 0.5rem;">
                            <div class="event-expander-content">
                                <pre style="background-color: #f7fafc; padding: 1rem; border-radius: 0.375rem; overflow-x: auto;">{colorize_json(event['data'])}</pre>
                            </div>
                        </div> """, unsafe_allow_html=True)

# Footer (The final block for the footer )
st.markdown("""
<div class="footer">
    <p><strong>🏥 Multi-Agent Healthcare Assistant</strong></p>
    <p>Educational Demo Only • Not for Medical Use</p>
</div>
""", unsafe_allow_html=True)
