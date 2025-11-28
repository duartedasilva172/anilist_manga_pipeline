import sqlite3 
import streamlit as st 
import pandas as pd 
import sys, os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "top_manga.db")

# ----- Create Insert Manga View -----

def insert_manga_view():
    st.title("Insert New Manga Record")

    with st.form("insert_manga_form"):
        title_romaji = st.text_input("Title Romaji")
        title_english = st.text_input("Title English")
        average_score = st.slider("Score", 0.0, 10.0, step=0.1)
        start_year = st.number_input("Start Year", min_value=0, step= 1)
        status = st.selectbox("Status",["FINISHED", "RELEASING", "HIATUS", "CANCELLED"])
        chapters = st.text_input("Chapters")
        volumes = st.text_input("Volumes")
        genres = st.multiselect("Genres", ["Action", "Drama", "Fantasy", "Comedy", "Romance", "Sci-Fi", "Slice of Life", "Adventure"])
        staff_input = st.text_area("Staff (format: name,occupation per line)", help = "e.g. \nNaoki Urasawa, Author\nJohn Doe,Editor")

        submit = st.form_submit_button("Insert Manga")

        if submit:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("""
                            INSERT OR REPLACE INTO top_manga (title_romaji, title_english, average_score, start_year, status, chapters, volumes) VALUES (?, ?, ?, ? ,?, ?, ?) """, 
                            (title_romaji, title_english, average_score, start_year, status, chapters, volumes))
                manga_id = cur.lastrowid  # Capture auto-generated ID

                # Insert genres
                for genre in genres: 
                    cur.execute("INSERT OR REPLACE INTO top_manga_genres (manga_id, genre) VALUES (?, ?)", (manga_id, genre))

                # Insert Staff
                for line in staff_input.strip().splitlines():
                    if ',' in line:
                        name, role = line.split(',',1)
                        cur.execute("INSERT OR REPLACE INTO top_manga_staff (manga_id, staff_name, occupation) VALUES (?, ?, ?)",
                                    (manga_id, name.strip(), role.strip()))


                conn.commit()
                st.success(f"Manga '{title_english}' inserted successfully.")
            except Exception as e:
                st.error(f"Insert failed: {e}")
            finally:
                conn.close()
