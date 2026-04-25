import pandas as pd
import psycopg2

# ── Your local DB connection ──────────────────────
conn = psycopg2.connect(
    host     = "localhost",
    port     = 5432,
    database = "india_location_db",
    user     = "postgres",
    password = "root"
)
cursor = conn.cursor()

# ── Loading cleaned CSV ──────────────────────────────
print("Reading CSV...")
df = pd.read_csv("india_villages_cleaned.csv")
print(f"Total rows: {len(df):,}")

# ──FOR INSERTING STATES ─────────────────────────────────
print("\nLoading states...")
states = df[['state_code','state_name']].drop_duplicates()
for _, row in states.iterrows():
    cursor.execute("""
        INSERT INTO states (code, name)
        VALUES (%s, %s)
        ON CONFLICT (code) DO NOTHING
    """, (int(row['state_code']), row['state_name']))
conn.commit()
print(f"  Done — {len(states)} states loaded")

# ── INSERTING DISTRICTS ──────────────────────────────
print("Loading districts...")
districts = df[['district_code','district_name','state_code']].drop_duplicates()
for _, row in districts.iterrows():
    cursor.execute("SELECT id FROM states WHERE code = %s", (int(row['state_code']),))
    state = cursor.fetchone()
    if state:
        cursor.execute("""
            INSERT INTO districts (code, name, state_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (code) DO NOTHING
        """, (int(row['district_code']), row['district_name'], state[0]))
conn.commit()
print(f"  Done — {len(districts)} districts loaded")

# ── INSERTING SUB DISTRICTS ──────────────────────────
print("Loading sub-districts...")
subdists = df[['subdistrict_code','subdistrict_name','district_code']].drop_duplicates()
for _, row in subdists.iterrows():
    cursor.execute("SELECT id FROM districts WHERE code = %s", (int(row['district_code']),))
    district = cursor.fetchone()
    if district:
        cursor.execute("""
            INSERT INTO sub_districts (code, name, district_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (code) DO NOTHING
        """, (int(row['subdistrict_code']), row['subdistrict_name'], district[0]))
conn.commit()
print(f"  Done — {len(subdists)} sub-districts loaded")

# ── INSERTING VILLAGES ───────────────────────────────
print("Loading villages... (this will take 2-3 mins)")
count = 0
for _, row in df.iterrows():
    cursor.execute("SELECT id FROM sub_districts WHERE code = %s", (int(row['subdistrict_code']),))
    subdist = cursor.fetchone()
    if subdist:
        cursor.execute("""
            INSERT INTO villages (code, name, sub_district_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (code) DO NOTHING
        """, (int(row['village_code']), row['village_name'], subdist[0]))
    count += 1
    if count % 50000 == 0:
        conn.commit()
        print(f"  {count:,} rows done...")

conn.commit()
print(f"  Done — villages loaded!")

# ── FINAL COUNT CHECK ─────────────────────────────
print("\n" + "="*45)
print("VERIFICATION")
print("="*45)
for table in ['states', 'districts', 'sub_districts', 'villages']:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table:<20} : {cursor.fetchone()[0]:,} rows")

cursor.close()
conn.close()
print("\nAll done! Database is ready.")