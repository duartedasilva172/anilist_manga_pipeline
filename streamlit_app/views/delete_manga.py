import streamlit as st 
import pandas as pd 
import sys, os 
import sqlite3 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "top_manga.db")

# ----- Delete Manga View -----

def delete_manga_view():
    st.title("Delete Manga Record")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    df = pd.read_sql("SELECT id, title_english FROM top_manga ORDER BY title_english", conn)

    if df.empty:
        st.warning("No manga records found")
        conn.close()
        return
    
    manga_map = dict(zip(df["title_english"], df["id"]))
    selected_title = st.selectbox("Select a Manga to delete", list(manga_map.keys()))
    selected_id = manga_map[selected_title]

    record = pd.read_sql("SELECT * FROM top_manga WHERE id = ?", conn, params=(selected_id,))
    with st.expander("View Manga Record"):
        st.dataframe(record)

    confirm = st.checkbox(f"Yes, I want to delete '{selected_title}'")

    if confirm:
        if st.button("Delete Now"):
            try:
                cur.execute("DELETE FROM top_manga WHERE id = ?",(selected_id,))
                conn.commit()
                st.success(f"Manga '{selected_title}' was deleted.")
            except Exception as e:
                st.error(f"Deletion failed : {e}")
            finally:
                conn.close()
