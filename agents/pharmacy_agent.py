# agents/pharmacy_agent.py
import pandas as pd
import json
from utils import haversine_km

class PharmacyAgent:
    def __init__(self, pharmacies_json='data/pharmacies.json', inventory_csv='data/inventory.csv', event_log=None):
        with open(pharmacies_json, 'r') as f:
            self.pharmacies = json.load(f)
        self.inventory_df = pd.read_csv(inventory_csv)
        self.log = event_log

    def find_nearest_with_stock(self, patient_lat, patient_lon, sku, qty=1):
        candidates = []
        for p in self.pharmacies:
            dist = haversine_km(patient_lat, patient_lon, p['lat'], p['lon'])
            if dist <= p.get('delivery_km', 10):
                inv = self.inventory_df[(self.inventory_df['pharmacy_id']==p['id']) & (self.inventory_df['sku']==sku)]
                if not inv.empty and int(inv.iloc[0]['qty']) >= qty:
                    candidates.append((p, float(inv.iloc[0]['price']), int(inv.iloc[0]['qty']), dist))
        if not candidates:
            return None
        candidates = sorted(candidates, key=lambda x: (x[1], x[3]))
        chosen = candidates[0]
        pharmacy, price, available_qty, dist_km = chosen
        eta_min = int(10 + 5 * dist_km)
        delivery_fee = 25 if dist_km < 10 else 50
        out = {
            "pharmacy_id": pharmacy['id'],
            "pharmacy_name": pharmacy['name'],
            "items": [{"sku": sku, "qty": qty, "price": price}],
            "eta_min": eta_min,
            "delivery_fee": delivery_fee,
            "distance_km": round(dist_km, 2)
        }
        if self.log:
            self.log.log("PharmacyAgent", "Matched pharmacy", out)
        return out

    def reserve_items(self, pharmacy_id, sku, qty=1):
        mask = (self.inventory_df['pharmacy_id']==pharmacy_id) & (self.inventory_df['sku']==sku)
        if mask.any():
            idx = self.inventory_df[mask].index[0]
            cur_qty = int(self.inventory_df.at[idx, 'qty'])
            if cur_qty >= qty:
                self.inventory_df.at[idx, 'qty'] = cur_qty - qty
                if self.log:
                    self.log.log("PharmacyAgent", f"Reserved {qty} of {sku} at {pharmacy_id}")
                return True
        return False