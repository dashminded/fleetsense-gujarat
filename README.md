# FleetSense Gujarat
### Demand-Driven Bus Fleet Optimization for Gujarat Private Operators

[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live%20App-red?logo=streamlit)](LIVE_LINK_HERE)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)](https://mysql.com)
[![Prophet](https://img.shields.io/badge/Prophet-Forecasting-blue)](https://facebook.github.io/prophet)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow?logo=powerbi)](https://powerbi.microsoft.com)

**Live App:** https://fleetsense.streamlit.app/

---

## Problem Statement

Gujarat's private bus operators (Patel Travels, Swaminarayan Travels, etc.) deploy
buses based on intuition — no data system exists for route-level planning.
This causes two losses simultaneously:

- **Weekdays:** Buses run 50–60% empty → wasted fuel, driver cost, toll cost
- **Festivals (Navratri, Diwali, Uttarayan):** Buses 100% full, passengers
  turned away → lost revenue, poor customer experience

No affordable demand forecasting tool exists for small/mid-size Gujarat
private operators. This project builds one.

---

## What This Project Does

Given a **route** and a **date**, FleetSense tells the operator:
- How full the bus is expected to be (forecasted occupancy %)
- How many buses to deploy (Add 2 / Add 1 / Keep / Remove 1)
- Estimated revenue gain or cost saved from that decision (₹)

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Data Generation | Python — Pandas, NumPy |
| Database | MySQL 8.0 (4 tables, 12 business queries) |
| EDA + Forecasting | Jupyter Notebook — Pandas, Seaborn, Plotly, Prophet |
| Dashboard | Power BI Desktop (7 visuals) |
| Web App | Streamlit — deployed on Community Cloud |

---

## Dataset

> **Synthetic data** simulated from real-world research — ticket prices from
> AbhiBus/RedBus listings, actual Gujarat festival dates (2023–2024), real
> fuel economics (diesel ₹95/L, Non-AC = 4.5 kmpl, AC = 2.65 kmpl).
> The same pipeline works on real operator data with zero code changes.

| File | Rows | Description |
|------|------|-------------|
| `routes.csv` | 12 | 12 Gujarat intercity routes with distance, tier, base price |
| `bus_inventory.csv` | 59 | 59 buses — 4 types (Non-AC/AC Seater/Sleeper) |
| `festivals.csv` | 33 | Real Gujarat festivals 2023–2024 with demand multipliers |
| `daily_bookings.csv` | 43,129 | Main fact table — every bus, every route, every day |

**Routes covered:**
AMD→Surat · AMD→Rajkot · AMD→Vadodara · AMD→Bhuj · AMD→Jamnagar ·
AMD→Junagadh · AMD→Dwarka · AMD→Somnath · AMD→Porbandar · AMD→Gandhidham ·
Rajkot→Surat · Surat→Vadodara

**Simulated business scale:** ₹72 Cr revenue · ₹41 Cr cost · ₹30 Cr profit (2 years)

---

## Prophet Forecast Accuracy

Trained on Jan 2023 – Sep 2024 | Tested on Oct – Dec 2024 (held-out quarter)

| Route | MAE | RMSE |
|-------|-----|------|
| AMD→Gandhidham | 12.99% | 15.67% |
| AMD→Bhuj | 11.23% | 15.19% |
| AMD→Dwarka | 6.47% | 9.72% |
| AMD→Jamnagar | 6.24% | 9.50% |
| AMD→Porbandar | 6.46% | 9.27% |
| Rajkot→Surat | 6.24% | 9.15% |
| AMD→Somnath | 5.88% | 9.06% |
| AMD→Junagadh | 5.99% | 8.96% |
| AMD→Surat | 4.84% | 8.89% |
| Surat→Vadodara | 5.74% | 8.84% |
| AMD→Rajkot | 4.66% | 8.47% |
| AMD→Vadodara | 4.88% | 8.47% |

> MAE and RMSE reported on occupancy rate (0.0–1.0 scale).
> e.g. RMSE = 0.06 means forecast is off by ~6 percentage points on average.

---

## Screenshots

### Streamlit App — Single Day Forecast
![Streamlit App](screenshots/streamlit_forecast.png)

### Streamlit App — Route Analytics
![Route Analytics](screenshots/streamlit_analytics.png)

### Power BI Dashboard
![Power BI](screenshots/powerbi_dashboard.png)

---

##  SQL Layer

**Database:** `fleetsense_gujarat` | **Tables:** `routes`, `bus_inventory`, `festivals`, `daily_bookings`

12 business queries covering:

| # | Query | SQL Concept Used |
|---|-------|-----------------|
| Q3 | Festival vs normal day revenue | `CASE WHEN` |
| Q5 | Monthly revenue trend 2023 vs 2024 | `GROUP BY year, month` |
| Q7 | Loss-making trips % per route | Conditional aggregation |
| Q9 | Fuel cost as % of revenue | Calculated ratio |
| Q11 | Fleet recommendation frequency | `GROUP BY` + percentage |
| Q12 | Day-of-week demand rank per route | `RANK() OVER (PARTITION BY)` |

---

##  Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/fleetsense-gujarat
cd fleetsense-gujarat

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Streamlit app
streamlit run fleetsense_app.py

# 4. Open Jupyter notebook
jupyter notebook notebook/FleetSense_Gujarat.ipynb

# 5. Import SQL (MySQL Workbench)
# Run sql/fleetsense_gujarat.sql → then import CSVs from data/ folder
```

---

##  Project Structure

```
fleetsense-gujarat/
│
├── data/
│   ├── routes.csv
│   ├── bus_inventory.csv
│   ├── festivals.csv
│   ├── daily_bookings.csv
│   └── fleet_forecast_90days.csv    ← Prophet output → Power BI input
│
├── notebook/
│   └── FleetSense_Gujarat.ipynb     ← EDA + Prophet model (6 sections)
│
├── sql/
│   └── fleetsense_gujarat.sql       ← CREATE TABLE + 12 business queries
│
├── screenshots/
│   ├── streamlit_forecast.png
│   ├── streamlit_analytics.png
│   └── powerbi_dashboard.png
│
├── generate_dataset.py              ← Reproduces all 4 CSVs from scratch
├── fleetsense_app.py                ← Streamlit app (3 tabs)
├── requirements.txt
└── README.md
```

---

## Key Business Insights

- **Navratri + Diwali** push occupancy 30%+ above the normal day average —
  adding 2 buses on major routes during these periods generates ~₹8,000–14,000
  net profit per route per day
- **Monday/Tuesday** are lowest demand days across all routes — removing 1 bus
  saves ~₹4,200/day in fuel + driver cost on Tier2/Tier3 routes
- **Rann Utsav (Nov–Feb)** creates sustained 50% demand increase on AMD→Bhuj
  and AMD→Gandhidham specifically — a pattern only visible with regional data
- **AMD→Surat** needs an extra bus 34% of all operating days — highest
  deployment pressure of any route in the network

---

##  About

**Ashutosh** — MCA Fresher | Ahmedabad, Gujarat | Targeting Data Analyst roles

This project was self-initiated after observing how Gujarat private bus
operators manage fleets without any data infrastructure.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)]www.linkedin.com/in/ashutosh772
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)]https://github.com/dashminded
