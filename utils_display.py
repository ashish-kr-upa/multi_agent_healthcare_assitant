# utils_display.py
import streamlit as st
import plotly.express as px

import json
import re

def colorize_json(data):
    """Convert dict to JSON with HTML color coding."""
    text = json.dumps(data, indent=2)

    # Highlight JSON elements
    #text = re.sub(r'\"(.*?)\"(?=\s*:)', r'<span style="color:#4FC3F7;">"\1"</span>', text)  # Keys
    text = re.sub(r'\"(.*?)\"', r'<span style="color:#A5D6A7;">"\1"</span>', text)           # Strings
    text = re.sub(r'\b(\d+)\b', r'<span style="color:#FFB74D;">\1</span>', text)            # Numbers
    text = re.sub(r'\b(true|false|null)\b', r'<span style="color:#CE93D8;">\1</span>', text, flags=re.IGNORECASE)  # Booleans

    return text


def display_metric_card(title, value, subtitle, color="#2b6cb0"):
    """Display a metric card with custom styling"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def display_agent_card(title, content, card_type="default"):
    """Display an agent card with proper styling"""
    st.markdown(f"""
    <div class="card {f'card-{card_type}' if card_type != 'default' else ''}">
        <h4 class="card-title">{title}</h4>
        {content}
    </div>
    """, unsafe_allow_html=True)


def display_medication_card(med):
    """Display a medication card with proper formatting"""
    warnings = med.get("warnings", [])
    warning_text = " ".join(warnings) if warnings else "No warnings"

    return f"""
    <div class="medication-card">
        <h4 class="medication-title">{med['drug_name']} (SKU: {med['sku']})</h4>
        <p class="medication-detail"><strong>Dosage:</strong> {med['dose']}</p>
        <p class="medication-detail"><strong>Frequency:</strong> {med['freq']}</p>
        <div class="medication-warning">{warning_text}</div>
    </div>
    """


def display_pharmacy_card(pharmacy, reserved=False):
    """Display a pharmacy card with proper formatting"""
    status = "Reserved" if reserved else "Available"
    status_class = "status-reserved" if reserved else "status-available"

    return f"""
    <div class="pharmacy-card">
        <h4 class="pharmacy-title">{pharmacy['pharmacy_name']} (ID: {pharmacy['pharmacy_id']})</h4>
        <p class="pharmacy-detail"><strong>Distance:</strong> {pharmacy['distance_km']} km</p>
        <p class="pharmacy-detail"><strong>ETA:</strong> {pharmacy['eta_min']} minutes</p>
        <p class="pharmacy-detail"><strong>Delivery Fee:</strong> ${pharmacy['delivery_fee']}</p>
        <div class="pharmacy-status {status_class}">{status}</div>
    </div>
    """


def create_probability_chart(probs):
    """Create a probability chart for imaging results"""
    fig = px.bar(
        x=list(probs.keys()),
        y=list(probs.values()),
        labels={"x": "Condition", "y": "Probability"},
        title="Condition Probabilities",
        color=list(probs.values()),
        color_continuous_scale=["#bee3f8", "#2b6cb0"]
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="#2c5282"
    )
    return fig