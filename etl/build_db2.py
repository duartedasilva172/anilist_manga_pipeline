import sqlite3
import pandas as pd 
import random
import os 
import numpy as np 
import ast 

# --- Set paths to database ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "top_manga2.parquet")
DB_PATH = os.path.join(BASE_DIR, "..", "db", "top_manga2.db")

print("Resolved Path:", os.path.abspath(DATA_PATH))
print("File exists?:", os.path.exists(DATA_PATH))

# --- Load data as CSV file ---

top_manga = pd.read_parquet(DATA_PATH)
print(type(top_manga["staff_names"].iloc[0]))
print(top_manga["staff_names"].head(3))
print("COLUMNS:",top_manga.columns)
print(top_manga.info)
print(top_manga.describe(include='all'))

print("Dataframe:", top_manga.head(20))

# --- Handle NULLS --- 

print("BEFORE:",top_manga.isna().sum())

top_manga["title_english"] = top_manga["title_english"].fillna("Not Recorded").astype(str)
top_manga["chapters"] = top_manga["chapters"].fillna(0).astype(float)
top_manga["volumes"] = top_manga["volumes"].fillna(0).astype(float)

print("AFTER:",top_manga.isna().sum())

print("Staff:",top_manga["staff_names"].head(10))


# --- Transform numpy arrays into lists ---

top_manga["staff_names"] = top_manga["staff_names"].apply(
    lambda x: list(x) if isinstance(x, np.ndarray) else x
)


# --- Transform Authors Occupations to Lists --- 

def fix_occupations(staff_list):
    if not isinstance(staff_list, list):
        return staff_list
    fixed = []
    for p in staff_list:
        occ = p.get("primaryOccupations", [])
        if isinstance(occ, np.ndarray):
            p["primaryOccupations"] = list(occ)
        fixed.append(p)
    return fixed

top_manga["staff_names"] = top_manga["staff_names"].apply(fix_occupations)

# --- Normalize Staff & Create Dataframe --- 

staff_rows = [] 

for _, row in top_manga.iterrows():
    manga_id = row["manga_id"]
    staff_list = row["staff_names"]

    if not isinstance(staff_list, list):
        continue

    for person in staff_list:
        name = person.get("name")
        occupations = person.get("primaryOccupations")

        if not occupations:
            staff_rows.append({
                "manga_id": manga_id,
                "staff_name": name,
                "occupation": "Not Recorded"
            })
        else:
            for occ in occupations:
                staff_rows.append({
                    "manga_id": manga_id,
                    "staff_name": name,
                    "occupation": occ
                })

staff_df = pd.DataFrame(staff_rows) # Save to dataframe 

