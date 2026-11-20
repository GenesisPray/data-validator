# 🏛️ MedBalance — Health Supply Chain Data Quality Assurance Platform

An institutional, enterprise-grade inventory data quality management (DQM) platform designed for government health agencies, public health programmes (e.g., Global Fund, USAID GHSC-PSM, WHO initiatives), and national supply chain management teams.

The system performs mathematical reconciliation on health facility commodity balance reports, audits physical stock conservation, identifies leakages and inventory reporting errors, classifies facilities by tier (**Primary Health Centre [PHC]** vs. **Health Centre [HC]**), and exports audit trails to `flagged.csv`.

---

## 🎨 Enterprise Design Specification

Following institutional public health guidelines:
- **Clean & Minimal Aesthetic**: High-contrast, executive-ready interface with zero visual noise.
- **Color Hierarchy**:
  - **Background**: Clean, crisp slate-50 (`#f8fafc`) with pure white card surfaces (`#ffffff`).
  - **Primary**: Deep institutional navy (`#0a1628` and `#0f2744`) for authority, typography, and primary actions.
  - **Accents**: Subtle clinical teal/emerald (`#0d9488` / `#0f766e`) for balanced stock and compliance states.
  - **Discrepancies**: High-visibility clinical red (`#dc2626` / `#b91c1c`) on soft `#fef2f2` for deficits and mathematical imbalances.
  - **Warnings**: Restrained amber (`#d97706` / `#b45309`) on soft `#fffbeb` for count surpluses and moderate variances.
- **Card Design**: Rounded cards (`8px` radius) with subtle, non-intrusive box shadows.
- **Data Rigor**: Monospace tabular numerals (`font-variant-numeric: tabular-nums`) to ensure strict columnar financial alignment.

---

## 🚀 Quick Access

### 🌐 Local Background Server
The application is running live at:
👉 **[http://localhost:8000](http://localhost:8000)** (or [http://127.0.0.1:8000](http://127.0.0.1:8000))

### 💻 Standalone Offline Browser
You can also directly open [`index.html`](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/index.html) in any browser without requiring an active server process.

---

## 🧮 Stock Reconciliation Audit Equation

Physical stock conservation rule enforced across all line items:

$$\text{Calculated Ending Balance} = \text{Beginning Balance} + \text{Received} - \text{Dispensed} - \text{Losses / Adjustments}$$

- **Audit Compliant**: $\text{Reported Physical Count} == \text{Calculated Ending Balance}$
- **Flagged Discrepancy**: $\text{Reported Physical Count} \neq \text{Calculated Ending Balance}$ or $\text{Calculated Ending Balance} < 0$ (negative physical stock).

---

## 📱 Navigation & Core Views

1. **Audit & Review (Home)**:
   - **Executive KPI Strip**: Total audited lines, balanced compliance %, flagged discrepancy count, and affected facilities count.
   - **Facility Classification Filter**: Segmented control for `All Levels`, `PHC` (Primary Health Centre), and `HC` (Health Centre / Hospital).
   - **Facility Searchable Selector**: Dropdown to isolate specific facilities with discrepancy counts.
   - **File Ingestion Strip**: Dropzone & metadata banner with single-click sample dataset loader.
   - **Audit Review Table**: High-density table featuring opening stock, additions, consumption, losses, calculated balance, reported count, and highlighted variance.
   - **Audit Trail Inspector**: Modal showing the complete step-by-step arithmetic and LMIS supervisory recommendations.
   - **Export flagged.csv**: UTF-8 BOM encoded CSV export ready for Microsoft Excel.

2. **Facility Performance Scorecard**:
   - Comprehensive facility registry tracking compliance rates and risk tiers (Compliant, Moderate Variance, High Risk).
   - Discrepancy frequency progress bars.
   - One-click record filtering per facility.

3. **Commodity Discrepancies**:
   - Comparative analytics between Primary Health Centres (PHC) and Health Centres (HC).
   - Categorization of errors (Shortage Deficits vs. Excess Surpluses vs. Negative Balances).
   - High-risk commodity leakage breakdown.

4. **Audit SOP & Mapping Guide**:
   - Standard Operating Procedures (SOP) documentation.
   - Automatic column synonym recognition matrix (compatible with eLMIS, DHIS2, and mSupply).
   - Blank CSV template generator.

---

## 📂 Workspace Structure

- [index.html](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/index.html): Enterprise Single-Page Application (SPA).
- [server.py](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/server.py): Background Python web server & API.
- [validator.py](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/validator.py): Stock conservation reconciliation engine.
- [validate_cli.py](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/validate_cli.py): Command-line batch audit tool.
- [sample_inventory_data.csv](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/sample_inventory_data.csv): 120-row demo dataset.
- [template_inventory.csv](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/template_inventory.csv): Blank CSV template.
- [flagged.csv](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/flagged.csv): Audit output containing flagged imbalanced rows.
- [run_app.bat](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/run_app.bat) / [run_app.ps1](file:///c:/Users/DELL%20PC/Desktop/Data%20Validator/run_app.ps1): Windows launchers.
