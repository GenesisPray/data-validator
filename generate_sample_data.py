"""
Generate sample dataset for testing the Data Validator Web App.
Includes realistic commodities, PHC and HC facilities, balanced rows and various flagged discrepancies.
"""

import csv
import random

FACILITIES = [
    ("Sunrise PHC", "PHC"),
    ("Greenfield PHC", "PHC"),
    ("Riverside PHC", "PHC"),
    ("Hope Community PHC", "PHC"),
    ("Harmony Rural PHC", "PHC"),
    ("Oak Valley PHC", "PHC"),
    ("St. Jude Health Centre", "HC"),
    ("Central City HC", "HC"),
    ("Victoria Memorial HC", "HC"),
    ("North Metro HC", "HC"),
    ("Highland District HC", "HC"),
    ("Mercy General HC", "HC"),
]

COMMODITIES = [
    "Artemether-Lumefantrine 20/120mg Tabs (AL)",
    "Amoxicillin 500mg Caps",
    "Oral Rehydration Salts (ORS) Sachets",
    "Zinc Sulfate 20mg Dispersible Tabs",
    "Paracetamol 500mg Tabs",
    "Oxytocin 10 IU/ml Ampoules",
    "Malaria Rapid Diagnostic Test (mRDT) Kits",
    "Depo-Provera (DMPA-IM) 150mg/ml",
    "Ferrous Sulfate 200mg + Folic Acid 0.4mg",
    "Cotrimoxazole 480mg Tabs",
    "HIV 1/2 Rapid Test Kits",
    "Male Condoms (Pieces)"
]

def generate_sample_csv(filename: str = "sample_inventory_data.csv", total_records: int = 120):
    rows = []
    
    for i in range(total_records):
        fac_name, fac_type = random.choice(FACILITIES)
        commodity = random.choice(COMMODITIES)
        
        bb = random.randint(50, 800)
        rec = random.choice([0, 50, 100, 200, 300, 500])
        # Dispensed usually <= bb + rec
        available = bb + rec
        disp = random.randint(10, min(available, 600))
        loss = random.choice([0, 0, 0, 2, 5, 10, 15])
        
        calculated_eb = bb + rec - disp - loss
        
        # Decide whether to introduce discrepancy (~35% chance)
        status_type = random.choices(
            ['balanced', 'surplus_error', 'deficit_error', 'negative_stock'],
            weights=[65, 15, 15, 5]
        )[0]
        
        if status_type == 'balanced':
            eb = calculated_eb
        elif status_type == 'surplus_error':
            # Counted more than mathematically possible
            error_diff = random.randint(5, 50)
            eb = calculated_eb + error_diff
        elif status_type == 'deficit_error':
            # Missing stock / unaccounted shortage
            error_diff = random.randint(5, 40)
            eb = max(0, calculated_eb - error_diff)
        elif status_type == 'negative_stock':
            # Dispensed more than physically available
            disp = available + random.randint(10, 45)
            calculated_eb = bb + rec - disp - loss
            eb = 0  # reported as 0 but negative mathematically
        
        rows.append({
            "Facility Name": fac_name,
            "Facility Type": fac_type,
            "Commodity": commodity,
            "Beginning Balance": bb,
            "Received": rec,
            "Dispensed": disp,
            "Losses Adjustment": loss,
            "Ending Balance": eb
        })

    with open(filename, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "Facility Name", "Facility Type", "Commodity",
            "Beginning Balance", "Received", "Dispensed",
            "Losses Adjustment", "Ending Balance"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} sample records in '{filename}'.")

if __name__ == "__main__":
    generate_sample_csv()

