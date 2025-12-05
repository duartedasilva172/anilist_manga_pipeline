import streamlit as st 
import pandas as pd 
import sqlite3
import sys, os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "top_manga2.db")
print("Connecting to db at:", DB_PATH)

# ----- Create Update View -----

def update_manga_view():
    st.title("Update Manga Record")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    df = pd.read_sql("SELECT manga_id, title_english FROM top_manga2 ORDER BY title_english", conn)

    if df.empty:
        st.warning("No manga records found")
        conn.close() 
        return
    
    manga_map = dict(zip(df["title_english"],df["manga_id"]))
    selected_title = st.selectbox("Select a Manga to edit", list(manga_map.keys()))
    selected_id = manga_map[selected_title]

    manga_data = pd.read_sql("SELECT * FROM top_manga2 WHERE manga_id = ?", conn, params=(selected_id,))
    manga = manga_data.iloc[0]

    with st.form("update_manga_form"):
        title_romaji = st.text_input("Romaji Title", value=manga["title_romaji"])
        title_english = st.text_input("English Title", value=manga["title_english"])
        format = st.text_input("Format (e.g. Manga, Light Novel)")
        popularity = st.number_input("Popularity", min_value=0, step=1)
        average_score = st.number_input("Score", 0, 100, value=int(manga["average_score"] or 0), step= 1)
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        status = st.selectbox("Status", ["FINISHED", "RELEASING","HIATUS", "CANCELLED"])
        chapters = st.text_input("Chapters",value=manga["chapters"])
        volumes = st.text_input("Volumes", value=manga["volumes"])
        genres = st.multiselect("Genres", ['Action', 'Adventure', 'Drama', 'Fantasy', 'Horror' ,'Psychological', 'Mystery',
                                            'Supernatural','Comedy' ,'Thriller' ,'Sports' ,'Sci-Fi' ,'Slice of Life',
                                            'Romance', 'Music', 'Mecha' ,'Ecchi' ,'Mahou Shoujo'])
        staff_input = st.text_area("Staff (format: name, occupation per line", help = "e.g. \nNaoki Urasawa, Author")

        submit = st.form_submit_button("Update Manga")

        if submit: 
            try:
                cur.execute("""
                    UPDATE top_manga2
                    SET title_romaji = ?, title_english = ?, format = ?, popularity = ?, average_score = ?,
                             start_date = ?, end_date = ?, status = ?, chapters = ?, volumes = ? 
                    WHERE id = ?
                """, (
                    title_romaji, 
                    title_english, 
                    format, 
                    popularity, 
                    average_score, 
                    start_date.isoformat(), 
                    end_date.isoformat(), 
                    status, 
                    chapters, 
                    volumes, 
                    selected_id
                ))
                
                # --- Update Genres ---
                cur.execute("DELETE FROM genre_2 WHERE manga_id = ?", (selected_id,))
                for genre in genres:
                    cur.execute("INSERT INTO genre_2 (manga_id, genre) VALUES (?, ?)", (selected_id, genre))

                # --- Update Staff ---
                cur.execute("DELETE FROM staff_2 WHERE manga_id = ?", (selected_id))
                for line in staff_input.strip().splitlines():
                    if ',' in line:
                        name, role = line.split(",", 1)
                        cur.execute("INSERT INTO staff_2 (manga_id, staff_name, occupation) VALUES (?, ?, ?)",
                                    (selected_id, name.strip(), role.strip()))
                conn.commit()
                st.success(f"{title_english}updated successfully")
            except Exception as e:
                st.error(f"Update Failed {e}")
            finally: 
                conn.close()


