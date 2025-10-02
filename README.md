# Multi-Agent Healthcare Assistant — Demo (Fresher Track)

**Prominent disclaimer:** **Educational demo — NOT medical advice.** This project is strictly for demonstration and learning. Do not use for clinical decisions. For emergencies, contact local emergency services immediately.

## What this repo contains
- A simple multi-agent demo (Python + Streamlit) with agents: Ingestion, Imaging (stub), Therapy, Pharmacy, Orchestrator.
- Dummy data under `/data` and a small in-memory reservation system (no persistent PHI storage).
- De-identification step that redacts basic PII patterns (emails, long numeric IDs, phone-like sequences).
- Unit tests under `/tests` (run with `pytest`).

## Quick local run (PyCharm / terminal)
Prerequisites:
- Python 3.10+ recommended
- git
- (optional) Tesseract OCR if you want OCR features: install tesseract on your machine for pytesseract to work.

Steps:
1. Download and unzip this project or clone your repo.
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # mac/linux
   venv\Scripts\activate    # windows (PowerShell)
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
5. Upload any PNG/JPG image as a 'chest X-ray' and click **Run triage & therapy**.

## Create GitHub repo & push (public, no login required to view)
1. In your terminal (project root):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - multi-agent demo"
   ```
2. Create a repository on GitHub (via UI) named e.g. `multi-agent-healthcare-demo` and copy the remote URL.
3. Add remote and push:
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/multi-agent-healthcare-demo.git
   git branch -M main
   git push -u origin main
   ```
Now your GitHub repo is public and can be connected to Streamlit Community Cloud.

## Deploy to Streamlit Community Cloud (Public app URL)
1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click "New app" → choose your repository and branch (main) → set the main file to `app.py` → Deploy.
3. Streamlit will provide a public app URL (no login required). Copy it to submit.

(Alternative: use Render.com or Railway; both can host simple Python web apps.)

## Deliverables mapping (what the assignment asked for)
1. Public app URL (create by deploying to Streamlit Cloud as described above).
2. README (this file) with setup, simple agent diagram, and safety/limitations.
3. Sample run: take screenshots while running the app locally (instructions below) + download sample order JSON from the UI when an order is created.
4. Tests: pytest tests are included under `/tests` (3 smoke tests).

## How to capture the required "Sample run" screenshots
1. Run the app locally with `streamlit run app.py`.
2. Upload a PNG/JPG, set age/allergies, and click **Run triage & therapy**.
3. Capture screenshots for:
   - Upload screen (showing uploaded files)
   - Results screen (showing ingestion/imaging/therapy/pharmacy/order outputs)
4. Save screenshots as `screenshots/step1_upload.png` and `screenshots/step2_results.png` and include them in your slide deck.

## Tests
Run tests with:
```bash
pytest -q
```
They are smoke tests to verify agent hand-offs.

## Safety & limitations
- The imaging component is a stub — no real medical predictions are made.
- Do not upload real PHI. De-identification is basic and meant for demo only.
- No prescriptions are suggested; therapy agent returns OTC options only.
- If low confidence or red flags are detected, the system recommends escalation to a mock doctor.

## Sample order JSON
When a mock order is created in the UI you can click **Download sample order JSON**. A sample file `sample_order.json` is also included in this repo for reference.

## Next steps / improvements
- Improve de-identification and PII safeguards.
- Replace imaging stub with an explainable lightweight model (careful with clinical claims).
- Persist inventory and orders to a small database for reproducible workflows.
