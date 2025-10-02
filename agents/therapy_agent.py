# agents/therapy_agent.py
import pandas as pd
import os


class TherapyAgent:
    def __init__(self, meds_csv_path='data/meds.csv', interactions_csv='data/interactions.csv', event_log=None):
        self.meds_df = pd.read_csv(meds_csv_path)
        try:
            self.inter_df = pd.read_csv(interactions_csv)
        except Exception:
            self.inter_df = None
        self.log = event_log

    def suggest_otc(self, conditions, patient):
        # pick top condition
        top = sorted(conditions.items(), key=lambda x: x[1], reverse=True)[0][0]
        suggestions = []
        for _, row in self.meds_df.iterrows():
            inds = str(row['indication']).split(';')
            if any(top.lower() in ind.lower() for ind in inds):
                if patient.get("age", 0) < int(row.get('age_min', 0)):
                    continue
                contra = str(row.get('contra_allergy_keywords', ''))
                allergies = patient.get("allergies", []) or []
                conflict = any(k.strip().lower() in (',').join(allergies).lower() for k in contra.split(',') if k)
                warnings = []
                if conflict:
                    warnings.append("Possible allergy/conflict with patient's allergy list.")
                suggestions.append({
                    "sku": row['sku'],
                    "drug_name": row['drug_name'],
                    "dose": "Follow label",
                    "freq": "As per label",
                    "warnings": warnings
                })

        # Fallback for pneumonia/covid if nothing found
        if not suggestions and top in ["pneumonia", "covid_suspect"]:
            suggestions.append({
                "sku": "OTC004",
                "drug_name": "ORS Solution",
                "dose": "1 sachet in water as needed",
                "freq": "Up to 3/day",
                "warnings": ["Supportive care only, see doctor if symptoms worsen"]
            })

        red_flags = []
        if 'chest pain' in (patient.get('notes', '') or '').lower():
            red_flags.append("Chest pain reported — advise immediate emergency care.")
        if 'shortness of breath' in (patient.get('notes', '') or '').lower():
            red_flags.append("Shortness of breath reported — advise immediate emergency care.")

        if self.log:
            self.log.log("TherapyAgent", "OTC suggestions computed",
                         {"suggestions": suggestions, "red_flags": red_flags})
        return {"otc_options": suggestions, "red_flags": red_flags}