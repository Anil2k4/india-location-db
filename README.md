# 🇮🇳 India Location DB — Data Pipeline & Admin Dashboard

> Production-grade data pipeline and admin dashboard for All India Villages API Platform.  
> Part of the **Capstone Project: All India Villages API** — B2B SaaS Platform.

---

## 📌 Project Overview

This repository contains the **Data Engineering and Analytics** component of the India Location API platform — a B2B SaaS service that provides structured, hierarchical address data for all Indian states, districts, sub-districts, and villages.

Businesses can integrate this API into:
- Address forms & dropdown menus
- KYC systems
- Logistics & delivery platforms
- E-commerce checkout flows

---

## 📊 Data Summary

| Level | Count |
|-------|-------|
| 🗺️ States | 29 |
| 🏙️ Districts | 530 |
| 🏘️ Sub-Districts | 5,313 |
| 🏡 Villages | 5,64,159 |

**Source:** MDDS (Ministry of Drinking Water and Sanitation) — Census 2011  
**Raw Files:** 30 Excel files (.xls / .ods), one per state

---

## 🗂️ Repository Structure

```
india-location-db/
├── combine.py                      # Step 1: Combines 30 state files into master CSV
├── load_data.py                    # Step 2: Cleans data + loads into PostgreSQL
├── dashboard.py                    # Step 3: Streamlit admin analytics dashboard
└── README.md                       # Project documentation
```

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Data processing & ETL |
| Pandas | Data cleaning & transformation |
| PostgreSQL | Normalized relational database |
| psycopg2 | Python → PostgreSQL connection |
| Streamlit | Interactive admin dashboard |
| Plotly | Charts & visualizations |
| GitHub | Version control & team collaboration |

---

## 🗄️ Database Schema

Follows **Third Normal Form (3NF)** normalization:

```
states
  └── districts          (FK → states.id)
        └── sub_districts  (FK → districts.id)
              └── villages   (FK → sub_districts.id)
```

### Tables

```sql
CREATE TABLE states (
    id    SERIAL PRIMARY KEY,
    code  INTEGER UNIQUE NOT NULL,
    name  VARCHAR(100) NOT NULL
);

CREATE TABLE districts (
    id        SERIAL PRIMARY KEY,
    code      INTEGER UNIQUE NOT NULL,
    name      VARCHAR(100) NOT NULL,
    state_id  INTEGER REFERENCES states(id)
);

CREATE TABLE sub_districts (
    id           SERIAL PRIMARY KEY,
    code         INTEGER UNIQUE NOT NULL,
    name         VARCHAR(100) NOT NULL,
    district_id  INTEGER REFERENCES districts(id)
);

CREATE TABLE villages (
    id               SERIAL PRIMARY KEY,
    code             INTEGER UNIQUE NOT NULL,
    name             VARCHAR(200) NOT NULL,
    sub_district_id  INTEGER REFERENCES sub_districts(id)
);
```

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install pandas xlrd odfpy psycopg2-binary streamlit plotly
```

### 2. Combine Raw Files
```bash
python combine.py
```
Reads all 30 state Excel files → outputs `india_villages_raw_master.csv`

### 3. Load into PostgreSQL
```bash
# First create the tables using the schema above in PgAdmin4
# Then update your DB password in load_data.py (line 8)
python load_data.py
```
Cleans data + loads all 4 tables into PostgreSQL

### 4. Run the Dashboard
```bash
streamlit run dashboard.py
```
Opens interactive dashboard at `http://localhost:8501`

---

## 📊 Dashboard Features

| Feature | Description |
|---------|-------------|
| 📌 KPI Cards | Total states, districts, sub-districts, villages |
| 📊 Top 10 States | Bar chart by village count |
| 🏙️ Districts Chart | All 29 states ranked |
| 🏘️ Sub-Districts Chart | Top 10 states |
| 📈 Avg Villages/District | Density analysis |
| 🔍 State Explorer | Interactive drill-down by state |
| 📋 Village Master List | Filter by state/district/sub-district + CSV download |

---

## 🧹 Data Cleaning Steps

| Step | Action | Records Affected |
|------|--------|-----------------|
| 1 | Removed junk header rows (MDDS PLCN = 0) | 5,987 removed |
| 2 | Dropped null rows | 53 removed |
| 3 | Removed duplicate village codes | 238 removed |
| 4 | Stripped trailing/leading whitespace | 4,753 fixed |
| 5 | Standardized casing (Title Case) | All 29 states |
| 6 | Dropped 6 unnamed junk columns | Cleaned |
| 7 | Renamed columns to clean snake_case | All columns |

**Before cleaning:** 5,70,438 rows  
**After cleaning:** 5,64,159 rows

---

## 🤝 Handoff to Backend Team

Backend team needs to:

1. Create a **NeonDB PostgreSQL** instance
2. Run the schema SQL to create 4 tables
3. Update connection string in `load_data.py`
4. Run `load_data.py` to populate NeonDB
5. Build REST APIs on top of the loaded data

### Sample API Queries (ready to use)

```sql
-- Get all states
SELECT id, code, name FROM states ORDER BY name;

-- Get districts by state
SELECT d.id, d.code, d.name
FROM districts d
JOIN states s ON s.id = d.state_id
WHERE s.name = 'Telangana';

-- Search villages
SELECT v.name, sd.name, d.name, s.name
FROM villages v
JOIN sub_districts sd ON sd.id = v.sub_district_id
JOIN districts d ON d.id = sd.district_id
JOIN states s ON s.id = d.state_id
WHERE v.name ILIKE '%kondapur%';
```

---

## 👤 Author

**Anil Varma** — Data/ETL Engineer  
B.Tech Computer Science | Hyderabad, India  
Skills: Python, SQL, PostgreSQL, Power BI, Data Analytics

---

## 📅 Project Timeline

| Date | Milestone |
|------|-----------|
| Apr 24, 2026 | Data extraction & cleaning complete |
| Apr 24, 2026 | PostgreSQL schema designed & loaded |
| Apr 25, 2026 | Admin dashboard built & deployed |
| Apr 25, 2026 | GitHub repository published |
| Apr 29, 2026 | Final project submission |
