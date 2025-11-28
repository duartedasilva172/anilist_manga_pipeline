import streamlit as st 
import pandas as pd 
import time 
import sys, os 
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "top_manga.db")

# Create connection


def run_sql_view():
    st.title("SQL Workbench")
    st.markdown("Enter any valid SQL query and click **Execute** to run it against the manga database.")

    query = st.text_area("SQL Query", height=200, placeholder="e.g., SELECT * FROM top_manga LIMIT 10;")

    if st.button("Execute"):
        if not query.strip():
            st.warning("Please enter SQL query.")
        else:
            try:
                conn_local = sqlite3.connect(DB_PATH)
                start = time.time()
                result = pd.read_sql(query, conn_local)
                end = time.time()

                st.success(f"Query executed in {end-start:.2f} seconds")
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Error: {e}")
            finally:
                conn_local.close()
