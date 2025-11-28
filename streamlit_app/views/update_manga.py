import streamlit as st 
import pandas as pd 
import sqlite3
import sys, os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "top_manga.db")
print("Connecting to db at:", DB_PATH)

# ----- Create Update View -----

def update_manga_view():
    st.title("Update Manga Record")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    df = pd.read_sql("SELECT id, title_english FROM top_manga ORDER BY title_english", conn)

    if df.empty:
        st.warning("No manga records found")
        conn.close() 
        return
    
    manga_map = dict(zip(df["title_english"],df["id"]))
    selected_title = st.selectbox("Select a Manga to edit", list(manga_map.keys()))
    selected_id = manga_map[selected_title]

    manga_data = pd.read_sql("SELECT * FROM top_manga WHERE id = ?", conn, params=(selected_id,))
    manga = manga_data.iloc[0]

    with st.form("update_manga_form"):
        title_romaji = st.text_input("Romaji Title", value=manga["title_romaji"])
        title_english = st.text_input("English Title", value=manga["title_english"])
        average_score = st.number_input("Score", 0, 100, value=int(manga["average_score"] or 0), step= 1)
        start_year = st.number_input("start_year", 0, 9999, value=int(manga["start_year"] or 0), step = 1)
        status = st.selectbox("Status", ["FINISHED", "RELEASING","HIATUS", "CANCELLED"])
        chapters = st.text_input("Chapters",value=manga["chapters"])
        volumes = st.text_input("Volumes", value=manga["volumes"])

        submit = st.form_submit_button("Update Manga")

        if submit: 
            try:
                cur.execute("""
                    UPDATE top_manga
                    SET title_romaji = ?, title_english = ?, average_score = ?, start_year = ?, status = ?, chapters = ?, volumes = ? 
                    WHERE id = ?
                """, (
                    title_romaji, title_english, average_score, start_year, status, chapters, volumes, selected_id
                ))
                conn.commit()
                st.success(f"{title_english}updated successfully")
            except Exception as e:
                st.error(f"Update Failed {e}")
            finally: 
                conn.close()


