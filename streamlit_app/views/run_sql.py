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

    # Optional Preset Queries 
    preset = st.selectbox("Load a preset query (optional):", [
        "-- Select an example --",
        "Top genres by average score",
        "Average score by year",
        "Top authors by score"
    ])

    default_query = ""

    if preset == "Top genres by average score":
        default_query = "SELECT g.genre, AVG(m.average_score) AS avg_score FROM top_manga m JOIN top_manga_genres g ON m.id = g.nanga_id GROUP BY g.genre ORDER BY avg_score DESC LIMI 20;"

    elif preset == "Average score by year":
        default_query = "SELECT start_year, AVG(average_score) AS avg_score FROM top_manga WHERE start_year IS NOT NULL GROUP BY start_year ORDER BY start_year DESC;"

    elif preset == "Top authors by score":
        default_query = "SELECT staff_name, AVG(average_score) AS avg_score FROM top_manga m JOIN top_manga_staff s ON m.id = s.manga_id WHERE s.occupation = 'Mangaka' GROUP BY staff_name ORDER BY avg_score DESC LIMIT 20;"

    
    query = st.text_area("SQL Query",value=default_query.strip(), height=200, placeholder="e.g., SELECT * FROM top_manga LIMIT 10;")

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

                    # Download CSV file button 
                    csv = result.to_csv(index= False).encode('utf-8')
                    st.download_button(
                        label = "Download Result as CSV.",
                        data = csv,
                        file_name="query_result.csv",
                        mime="text/csv"
                        )
            except Exception as e:
                    st.error(f"SQL Error: {e}")
            finally:
                    conn_local.close()
