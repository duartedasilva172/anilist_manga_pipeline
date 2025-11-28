import sqlite3
import pandas as pd
import random
import os 
import numpy as np
import ast

# ----- Set Paths to Database -----

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "top_manga.parquet")
DB_PATH = os.path.join(BASE_DIR, "..", "db","top_manga.db")

print("Resolved path:", os.path.abspath(DATA_PATH))
print("File Exists?", os.path.exists(DATA_PATH))

# ----- Load CSV File -----

top_manga = pd.read_parquet(DATA_PATH)
print(type(top_manga["staff_names"].iloc[0]))
print(top_manga["staff_names"].head(3))
print(top_manga.columns)
print(top_manga.info)
print(top_manga.describe(include='all'))

print(top_manga.head(10))

# ----- Check For NULLS -----

print(top_manga.isna().sum())

# Three columns (chapter, volumes, title_english) have more than 50 null values, given that these null values are not necessarily crucial, not recorded, or non-existing for the specific manga, 
# we can easily handle them by relacing them with "Not Recorded"

# ----- Replace Nulls with "Not Recorded" -----

top_manga["chapters"] = top_manga["chapters"].fillna("Not Recorded")
top_manga["volumes"] = top_manga["volumes"].fillna("Not Recorded")
top_manga["title_english"] = top_manga["title_english"].fillna("Not Recorded")

# ----- Check NULLS were handled -----

print(top_manga["chapters"].head(5), top_manga["volumes"].head(5), top_manga["title_english"].head(5))
print("Remaining NULL values:",top_manga.isna().sum())

# -----

top_manga["staff_names"] = top_manga["staff_names"].apply(
    lambda x: list(x) if isinstance(x, np.ndarray) else x
)

# ----- Fix numpy arrays inside staff dicts -----

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


# ----- Normalize 'staff' column -----

staff_rows = []

for _, row in top_manga.iterrows():
    manga_id = row["id"]
    staff_list = row["staff_names"]

    if not isinstance(staff_list, list):
        continue

    for person in staff_list:
        name = person.get("name")
        occupations = person.get("primaryOccupations", [])

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

top_manga = top_manga.drop(columns=["staff_names"]) # Drop staff column in original database 

# ----- Check Dataframes -----

print("Current Dataframes:", "Manga:",top_manga.head(10), "Staff:", staff_df.head(10))
print(top_manga["genres"].head(10))

# ----- Normalize Genres -----

print(type(top_manga["genres"].iloc[0]))
print(top_manga["genres"].head())

# Step 1: Flatten all genres with manga_id 

genres_flat = top_manga.explode("genres")[["id", "genres"]].dropna()
genres_flat.columns = ["manga_id", "genre"]

print("Normalized Genres:",genres_flat.head(10))
print("Normalized Staff:", staff_df.head(10))
print("Top Manga:", top_manga.head(10))
# ----- Create Database Connection -----

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ----- Create Top Manga Table -----

cur.execute("DROP TABLE IF EXISTS top_manga")


cur.execute("""
            CREATE TABLE IF NOT EXISTS top_manga(
            id INTEGER,
            title_romaji TEXT,
            title_english TEXT,
            average_score INTEGER, 
            start_year INTEGER,
            status TEXT,
            chapters TEXT,
            volumes TEXT,
            PRIMARY KEY (id)
            );
""")

# Convert top_manga DataFrame into a list of tuples 

top_manga_tuples = top_manga[["id", "title_romaji", "title_english", "average_score", "start_year", "status", "chapters", "volumes"
                     ]].itertuples(index=False, name=None)

# Insert into database 

cur.executescript(""" DELETE FROM top_manga;""")

cur.executemany("""
                INSERT OR REPLACE INTO top_manga (id, title_romaji, title_english, average_score, start_year, status, chapters, volumes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, top_manga_tuples)

cur.execute("SELECT * FROM top_manga LIMIT 15")
print(cur.fetchall())

# ----- Create Staff table -----

cur.execute("DROP TABLE IF EXISTS top_manga_staff")


print(staff_df.head(5))
cur.execute("""
         CREATE TABLE IF NOT EXISTS top_manga_staff(
            manga_id INTEGER,
            staff_name TEXT,
            occupation TEXT,
            PRIMARY KEY (manga_id, staff_name, occupation),
            FOREIGN KEY (manga_id) REFERENCES top_manga(id)
        );               
""")

# Convert staff_df into list of tuples 

staff_tuples = staff_df[["manga_id", "staff_name", "occupation"]].itertuples(index=False, name=None)

# Deletion

cur.executescript("""DELETE FROM top_manga_staff;""")



# Load into database 

cur.executemany("""
                INSERT OR REPLACE INTO top_manga_staff (manga_id, staff_name, occupation)
                VALUES (?, ?, ?)
                """, staff_tuples)

cur.execute("SELECT * FROM top_manga_staff LIMIT 10")
print(cur.fetchall())

# ----- Create Genres Table -----

# Drop previous table for total control

cur.execute("DROP TABLE IF EXISTS top_manga_genres")

print(genres_flat.head())

cur.execute("""
            CREATE TABLE IF NOT EXISTS top_manga_genres(
            manga_id INTEGER,
            genre TEXT,
            PRIMARY KEY (manga_id, genre),
            FOREIGN KEY (manga_id) REFERENCES top_manga(id)
            );
            """)

# Convert genres into a list of tuples 

genre_tuples = genres_flat[["manga_id", "genre"]].itertuples(index=False, name=None)

# Deletion

cur.executescript("""DELETE FROM top_manga_genres;""")


# Load into database 

cur.executemany("INSERT OR REPLACE INTO top_manga_genres(manga_id, genre) VALUES (?, ?)", genre_tuples)
cur.execute("SELECT * FROM top_manga_genres LIMIT 10")
print(cur.fetchall())

# ----- Commit & Close -----

conn.commit()
conn.close()
print("Database Successfully built at:", DB_PATH)
