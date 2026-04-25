import pandas as pd
import os

EXTRACT_FOLDER = "all-india-villages-master-list-excel"
OUTPUT_FILE = "india_villages_raw_master.csv"

folder = os.path.join(EXTRACT_FOLDER, "dataset")

if not os.path.exists(folder):
    folder = EXTRACT_FOLDER

all_dataframes = []

files = [f for f in os.listdir(folder) if f.endswith((".xls", ".ods"))]

print(f"Found {len(files)} files\n")

for file in files:
    path = os.path.join(folder, file)
    try:
        df = pd.read_excel(path)
        df["source_file"] = file
        all_dataframes.append(df)
        print(f"OK {file} → {len(df)} rows")
    except Exception as e:
        print(f"ERROR {file} → {e}")

master_df = pd.concat(all_dataframes, ignore_index=True)
master_df.to_csv(OUTPUT_FILE, index=False)

print("\nDONE ✅")
print("Saved file:", OUTPUT_FILE)