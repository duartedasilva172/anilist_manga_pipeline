import sqlite3 
import streamlit as st 
import pandas as pd 
import sys, os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "top_manga2.db")

# ----- Create Insert Manga View -----

def insert_manga_view():
    st.title("Insert New Manga Record")

    with st.form("insert_manga_form"):
        title_romaji = st.text_input("Title Romaji")
        title_english = st.text_input("Title English")
        format = st.text_input("Format (e.g. Manga, Light Novel)")
        popularity = st.number_input("Popularity", min_value=0, step=1)
        average_score = st.slider("Score", 0.0, 100.0, step=0.1)
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        status = st.selectbox("Status",["FINISHED", "RELEASING", "HIATUS", "CANCELLED"])
        chapters = st.number_input("Chapters", min_value=0, step=1)
        volumes = st.number_input("Volumes", min_value=0, step=1)
        genres = st.multiselect("Genres", ['Action' 'Adventure' 'Drama' 'Fantasy' 'Horror' 'Psychological' 'Mystery'
                                            'Supernatural' 'Comedy' 'Thriller' 'Sports' 'Sci-Fi' 'Slice of Life'
                                            'Romance' 'Music' 'Mecha' 'Ecchi' 'Mahou Shoujo'])
        staff_input = st.text_area("Staff (format: name,occupation per line)", help = "e.g. \nNaoki Urasawa, Author\nJohn Doe,Editor")

        submit = st.form_submit_button("Insert Manga")

        if submit:
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("""
                            INSERT OR REPLACE INTO top_manga (title_romaji, title_english, title_native, format, popularity, average_score, start_date, end_date, status, chapters, volumes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, 
                            (title_romaji, 
                             title_english,
                             format, 
                             average_score, 
                             start_date.isoformat(),
                             end_date.isoformat(),
                             status, 
                             chapters, 
                             volumes))
                manga_id = cur.lastrowid  # Capture auto-generated ID

                # Insert genres
                for genre in genres: 
                    cur.execute("INSERT OR REPLACE INTO genres_2 (manga_id, genre) VALUES (?, ?)", (manga_id, genre))

                # Insert Staff
                for line in staff_input.strip().splitlines():
                    if ',' in line:
                        name, role = line.split(',',1)
                        cur.execute("INSERT OR REPLACE INTO staff_2 (manga_id, staff_name, occupation) VALUES (?, ?, ?)",
                                    (manga_id, name.strip(), role.strip()))


                conn.commit()
                st.success(f"Manga '{title_english}' inserted successfully.")
            except Exception as e:
                st.error(f"Insert failed: {e}")
            finally:
                conn.close()
