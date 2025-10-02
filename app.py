# app.py
import streamlit as st
import os
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from agents.orchestrator import Orchestrator
from utils_display import (
    colorize_json,
    display_metric_card,
    display_agent_card,
    display_medication_card,
    display_pharmacy_card,
    create_probability_chart
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)

# Custom CSS with underline hover effects and no disclaimer box
st.markdown("""
<style>
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

    /* Event log with visible text - FIXED */
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

    /* Analytics specific styles - FIXED */
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

    /* Tabs styling with underline hover effects */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        border-bottom: 2px solid #e2e8f0;
        border-radius: 0;
        padding: 0;
        margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab"] {
        color: #4a5568;
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

    /* Sidebar styling */
    .sidebar-header {
        background-color: #ebf8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }

    .sidebar-header h3 {
        color: #2c5282;
        margin-top: 0;
    }

    .sidebar-section h4 {
        color: #2c5282;
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
st.markdown('<h1 class="main-header">🏥 Multi-Agent Healthcare Assistant</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="disclaimer">
    <strong>⚠️ Disclaimer:</strong> This is an <strong>educational demo only</strong>.  
    It is <strong>not medical advice</strong>. For emergencies, please contact local emergency services.
</div>
""", unsafe_allow_html=True)

# Sidebar inputs
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h3>🔧 Patient Information</h3></div>', unsafe_allow_html=True)

    uploaded_xray = st.file_uploader("📷 Chest X-ray (PNG/JPG)", type=["png", "jpg", "jpeg"])
    uploaded_pdf = st.file_uploader("📄 Report/ID (PDF, optional)", type=["pdf"])

    st.markdown('<div class="sidebar-section"><h4>🧑 Patient Details</h4></div>', unsafe_allow_html=True)
    age = st.number_input("Age", min_value=0, max_value=120, value=45)
    allergies = st.text_input("Allergies (comma separated)", value="ibuprofen")

    st.markdown('<div class="sidebar-section"><h4>📝 Symptoms & Notes</h4></div>', unsafe_allow_html=True)
    notes_input = st.text_area(
        "Enter symptoms, complaints, or doctor notes",
        placeholder="Example: cough and mild fever for 3 days",
        height=100
    )

    st.markdown('<div class="sidebar-section"><h4>📍 Location</h4></div>', unsafe_allow_html=True)
    patient_lat = st.number_input("Latitude", value=19.12, format="%.6f")
    patient_lon = st.number_input("Longitude", value=72.84, format="%.6f")

    run_button = st.button("🚀 Run Analysis", use_container_width=True)

# Main execution
if run_button:
    if not uploaded_xray:
        st.error("Please upload a chest X-ray image to continue.")
    else:
        # Save inputs
        xray_path = os.path.join("uploads", uploaded_xray.name)
        with open(xray_path, "wb") as f:
            f.write(uploaded_xray.read())

        pdf_path = None
        if uploaded_pdf:
            pdf_path = os.path.join("uploads", uploaded_pdf.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.read())

        patient_info = {
            "age": int(age),
            "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
            "notes": notes_input
        }

        orch = Orchestrator()
        with st.spinner("Processing through AI agents..."):
            plan = orch.run(
                xray_path,
                pdf_path=pdf_path,
                patient_info=patient_info,
                patient_lat=patient_lat,
                patient_lon=patient_lon
            )

        # Summary cards
        st.markdown("## 📊 Analysis Summary")
        condition_probs = plan["imaging"]["condition_probs"]
        top_condition = max(condition_probs, key=condition_probs.get)
        top_prob = condition_probs[top_condition]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            display_metric_card("Top Condition", top_condition.title(), f"Confidence: {top_prob:.0%}", color="#2b6cb0")
        with col2:
            esc = plan["doctor_escalation"]["recommended"]
            reasons = plan["doctor_escalation"].get("reasons", [])
            reason_text = reasons[0] if reasons else "No escalation needed"
            display_metric_card("Doctor Escalation", "Yes" if esc else "No", reason_text,
                                color="#f56565" if esc else "#48bb78")
        with col3:
            order = plan["order"]
            display_metric_card("Order Created", "Yes" if order else "No",
                                order["order_id"] if order else "No items ordered",
                                color="#48bb78" if order else "#718096")
        with col4:
            otc_count = len(plan["therapy"]["otc_options"])
            display_metric_card("OTC Options", str(otc_count), "Medications suggested", color="#ed8936")

        # Tabs with underline hover effects
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            ["📥 Ingestion", "📝 Notes", "🩻 Analytics", "💊 Therapy", "👨‍⚕️ Escalation", "🏪 Pharmacy", "📜 Event Log"]
        )

        with tab1:
            st.markdown("### 📥 Ingestion Results")
            patient = plan["ingestion"]["patient"]
            display_agent_card("Patient Information",
                               f"<p class='card-text'><span class='card-highlight'>Age:</span> {patient['age']}</p><p class='card-text'><span class='card-highlight'>Allergies:</span> {', '.join(patient['allergies']) or 'None'}</p>")
            display_agent_card("Uploaded Files",
                               f"<p class='card-text'><span class='card-highlight'>X-ray:</span> {os.path.basename(plan['ingestion']['xray_path'])}</p><p class='card-text'><span class='card-highlight'>PDF:</span> {os.path.basename(pdf_path) if pdf_path else 'None uploaded'}</p>")
            display_agent_card("Processing Details",
                               f"<p class='card-text'><span class='card-highlight'>Text Extracted:</span> {'Yes' if plan['ingestion']['notes_raw'] else 'No'}</p><p class='card-text'><span class='card-highlight'>PII Redacted:</span> {'Yes' if plan['ingestion']['notes'] != plan['ingestion']['notes_raw'] else 'No'}</p><p class='card-text'><span class='card-highlight'>Processing Time:</span> {datetime.now().strftime('%H:%M:%S')}</p>")

        with tab2:
            st.markdown("### 📝 Combined Notes")
            if plan["ingestion"].get("notes"):
                display_agent_card("Patient Notes (Manual + Extracted)",
                                   f"<p class='card-text'>{plan['ingestion']['notes']}</p>")
                if plan["ingestion"]["notes_raw"]:
                    with st.expander("View Raw Extracted Text"):
                        st.code(plan["ingestion"]["notes_raw"])
            else:
                st.info("No notes provided or extracted.")

        with tab3:
            st.markdown("### 🩻 Imaging Analytics & Insights")

            # Get imaging data
            probs = plan["imaging"]["condition_probs"]
            severity = plan["imaging"]["severity_hint"]
            model_info = plan["imaging"]["meta"]

            # Top row: Key metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="analytics-card">
                    <div class="analytics-title">
                        <div class="analytics-icon" style="background: rgba(66, 153, 225, 0.1); color: #4299e1;">
                            🎯
                        </div>
                        Primary Finding
                    </div>
                    <div class="analytics-content">
                        <div class="analytics-value">{top_condition.title()}</div>
                        <div class="confidence-meter">
                            <div class="confidence-fill" style="width: {top_prob * 100}%">
                                <span class="confidence-text">{top_prob:.0%}</span>
                            </div>
                        </div>
                        <div class="analytics-subtitle">Confidence Level</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                severity_colors = {
                    "mild": "#48bb78",
                    "moderate": "#ed8936",
                    "severe": "#f56565"
                }
                severity_icons = {
                    "mild": "✅",
                    "moderate": "⚠️",
                    "severe": "🚨"
                }

                st.markdown(f"""
                <div class="analytics-card">
                    <div class="analytics-title">
                        <div class="analytics-icon" style="background: rgba({severity_colors.get(severity, '#4a5568').replace('#', '')}, 0.1); color: {severity_colors.get(severity, '#4a5568')};">
                            {severity_icons.get(severity, '📊')}
                        </div>
                        Severity Assessment
                    </div>
                    <div class="analytics-content">
                        <div class="analytics-value" style="color: {severity_colors.get(severity, '#4a5568')};">{severity.title()}</div>
                        <div class="severity-indicator">
                            <div class="severity-marker" style="left: {'10%' if severity == 'mild' else '50%' if severity == 'moderate' else '90%'}; background: {severity_colors.get(severity, '#4a5568')};"></div>
                        </div>
                        <div class="analytics-subtitle">Risk Level Indicator</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                model_type = model_info.get('model', 'rule-based')
                model_icon = "🤖" if model_type == "CNN" else "📋"

                st.markdown(f"""
                <div class="analytics-card">
                    <div class="analytics-title">
                        <div class="analytics-icon" style="background: rgba(160, 174, 192, 0.1); color: #64748b;">
                            {model_icon}
                        </div>
                        Analysis Model
                    </div>
                    <div class="analytics-content">
                        <div class="analytics-value" style="color: #64748b; font-size: 1.5rem;">{model_type.title()}</div>
                        <div class="analytics-subtitle">Processing Method</div>
                        <div class="analytics-subtitle" style="font-size: 0.75rem; color: #718096;">{model_info.get('ts', 'Unknown time')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Second row: Charts
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📊 Condition Probability Distribution")
                # Create bar chart
                fig = px.bar(
                    x=list(probs.keys()),
                    y=list(probs.values()),
                    labels={"x": "Condition", "y": "Probability"},
                    color=list(probs.values()),
                    color_continuous_scale=["#bee3f8", "#2b6cb0"],
                    title="Condition Probabilities"
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color="#2c5282",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("#### 🥧 Probability Breakdown")
                # Create pie chart
                fig = px.pie(
                    values=list(probs.values()),
                    names=list(probs.keys()),
                    title="Condition Distribution",
                    color_discrete_map={
                        "normal": "#48bb78",
                        "pneumonia": "#ed8936",
                        "covid_suspect": "#f56565"
                    }
                )
                fig.update_layout(
                    font_color="#2c5282",
                    height=300,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=0,
                        xanchor="center",
                        x=0.5
                    )
                )
                st.plotly_chart(fig, use_container_width=True)

            # Third row: Detailed analysis
            st.markdown("#### 🔍 Detailed Analysis")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div class="analytics-card">
                    <div class="analytics-title">
                        <div class="analytics-icon" style="background: rgba(72, 187, 120, 0.1); color: #48bb78;">
                            📈
                        </div>
                        Statistical Summary
                    </div>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">
                        <tr>
                            <td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;"><strong>Condition</strong></td>
                            <td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;"><strong>Probability</strong></td>
                        </tr>
                """, unsafe_allow_html=True)

                for condition, prob in probs.items():
                    color = "#48bb78" if prob > 0.5 else "#ed8936" if prob > 0.3 else "#f56565"
                    st.markdown(f"""
                        <tr>
                            <td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0; color: #2c5282;">{condition.title()}</td>
                            <td style="padding: 0.5rem; border-bottom: 1px solid #e2e8f0;"><span style="color: {color}; font-weight: 600;">{prob:.1%}</span></td>
                        </tr>
                    """, unsafe_allow_html=True)

                st.markdown("</table></div>", unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="analytics-card">
                    <div class="analytics-title">
                        <div class="analytics-icon" style="background: rgba(245, 158, 11, 0.1); color: #ed8936;">
                            💡
                        </div>
                        Key Insights
                    </div>
                """, unsafe_allow_html=True)

                # Generate insights based on probabilities
                insights = []

                if top_prob > 0.7:
                    insights.append(("High Confidence",
                                     f"The model shows high confidence ({top_prob:.0%}) in detecting {top_condition}."))
                elif top_prob > 0.5:
                    insights.append(("Moderate Confidence",
                                     f"The model indicates {top_condition} with moderate confidence ({top_prob:.0%})."))
                else:
                    insights.append(("Low Confidence",
                                     f"The model shows low confidence ({top_prob:.0%}). Further evaluation recommended."))

                if severity == "severe":
                    insights.append(("Critical Alert",
                                     "Severity assessment indicates immediate medical attention may be required."))
                elif severity == "moderate":
                    insights.append(("Monitor Closely", "Condition requires careful monitoring and follow-up."))
                else:
                    insights.append(("Stable Condition", "Condition appears stable with low risk."))

                if probs.get("pneumonia", 0) > 0.5:
                    insights.append(
                        ("Infection Likely", "High probability of bacterial infection requiring treatment."))

                if probs.get("covid_suspect", 0) > 0.3:
                    insights.append(("COVID Screening", "Consider COVID-19 testing and isolation protocols."))

                for title, text in insights:
                    st.markdown(f"""
                    <div class="insight-box">
                        <div class="insight-title">{title}</div>
                        <div class="insight-text">{text}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

        with tab4:
            st.markdown("### 💊 Therapy Recommendations")
            if plan["therapy"]["red_flags"]:
                for flag in plan["therapy"]["red_flags"]:
                    display_agent_card("⚠️ Red Flag", f"<p class='card-text'>{flag}</p>", card_type="severe")
            for med in plan["therapy"]["otc_options"]:
                st.markdown(display_medication_card(med), unsafe_allow_html=True)

        with tab5:
            st.markdown("### 👨‍⚕️ Doctor Escalation")
            esc = plan["doctor_escalation"]
            if esc["recommended"]:
                reasons = "".join([f"<li>{r}</li>" for r in esc.get("reasons", [])])
                display_agent_card("Escalation Recommended", f"<ul class='card-text'>{reasons}</ul>",
                                   card_type="escalation-yes")
                if esc.get("doctor"):
                    doc = esc["doctor"]
                    display_agent_card("Assigned Doctor",
                                       f"<p class='card-text'><span class='card-highlight'>{doc['name']}</span> (ID: {doc['doctor_id']})<br><span class='card-highlight'>Slot:</span> {doc['tele_slot']}</p>")
            else:
                display_agent_card("No Escalation Required",
                                   "<p class='card-text'>Doctor escalation is not necessary at this time.</p>",
                                   card_type="escalation-no")

        with tab6:
            st.markdown("### 🏪 Pharmacy & Order Information")
            for match in plan["pharmacy_matches"]:
                if match["match"]:
                    st.markdown(display_pharmacy_card(match["match"], reserved=match["match"].get("reserved", False)),
                                unsafe_allow_html=True)
                else:
                    display_agent_card("No Pharmacy Found",
                                       f"<p class='card-text'>No match for SKU {match['sku']}.</p>")
            if plan["order"]:
                order = plan["order"]
                display_agent_card("Order Details",
                                   f"<p class='card-text'><span class='card-highlight'>Order ID:</span> {order['order_id']}</p><p class='card-text'><span class='card-highlight'>Items:</span> {len(order['items'])}</p>")
                st.download_button("⬇️ Download Order JSON", data=json.dumps(order, indent=2),
                                   file_name=f"order_{order['order_id']}.json", mime="application/json")
            else:
                st.info("No order created.")

        with tab7:
            st.markdown("### 📜 Event Log")
            # Event log with improved visibility
            for event in plan["event_log"][::-1][:20]:
                st.markdown(f"""
                <div class="event-log-item">
                    <span class="event-timestamp">{event['ts']}</span> - 
                    <span class="event-source">{event['source']}</span>: 
                    <span class="event-message">{event['message']}</span>
                </div>
                """, unsafe_allow_html=True)

                if event.get("data"):
                    expander_title = f"📋 View data from {event['source']}"
                    with st.expander(expander_title, expanded=False):
                        st.markdown(f"""
                        <div class="event-expander" 
                             style="background-color: #1E1E2F; 
                                    border: 1px solid #00BFFF; 
                                    border-radius: 0.375rem; 
                                    padding: 1rem; 
                                    margin-top: 0.5rem;">
                            <div class="event-expander-header" 
                                 style="color: #00BFFF; font-weight: bold; margin-bottom: 0.5rem;">
                                📊 Detailed Data from {event['source']}
                            </div>
                            <div class="event-expander-content" style="font-family: monospace; font-size: 0.9rem;">
                                <pre style="background-color: #2C2C3C; 
                                            padding: 1rem; 
                                            border-radius: 0.375rem; 
                                            overflow-x: auto;">{colorize_json(event['data'])}</pre>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p><strong>🏥 Multi-Agent Healthcare Assistant</strong></p>
    <p>Educational Demo Only • Not for Medical Use</p>
</div>
""", unsafe_allow_html=True)