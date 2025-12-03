import streamlit as st 
import sys, os 
import sqlite3

# ----- Define path for imports -----

os.path.exists("/Users/duartedasilva/Desktop/Data Work/Data Projects/db/top_manga.db")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
DB_PATH = os.path.join(os.path.dirname(__file__),"..", "db", "top_manga.db")


from views.run_sql import run_sql_view
from views.update_manga import update_manga_view
from views.insert_manga import insert_manga_view
from views.delete_manga import delete_manga_view
from views.dashboard_view import show_dashboard
from views.insights_view import show_insights

# ----- Main Menu -----

st.sidebar.title("Manga Explorer")

view = st.sidebar.radio("Choose a view:", ["Dashboard", "SQL Workbench", "Insights"])

if view == "Dashboard":
    show_dashboard()

elif view == "SQL Workbench":

    mode = st.sidebar.radio("Mode", ["SQL Workbench", "Insert Data", "Update Manga", "Delete Manga"])

# ----- Table Schemas -----

    def get_table_schemas():
       resolved_path = os.path.abspath(DB_PATH)
       st.write(f"Connected to DB at: {resolved_path}")
       with sqlite3.connect(resolved_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall()]

        table_schemas = {}
        for table in tables:
            cur.execute(f"PRAGMA table_info({table});")
            columns = [col[1] for col in cur.fetchall()]
            table_schemas[table] = columns
        return table_schemas
       

    if mode == "SQL Workbench":
        with st.expander("View Table Structures", expanded= True):
            st.image("streamlit_app/assets/db_schema.png", caption = "Manga Database Schema", use_container_width=True) 
        run_sql_view()

    if mode == "Update Manga":
        update_manga_view()

    if mode == "Insert Data":
        insert_manga_view()

    if mode == "Delete Manga":

        delete_manga_view()

elif view == "Insights":
    show_insights()