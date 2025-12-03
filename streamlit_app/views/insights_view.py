import streamlit as st 
import sqlite3 
import pandas as pd 
import altair as alt 
import sys, os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
DB_PATH = os.path.join(os.path.dirname(__file__),"..", "..", "db", "top_manga.db")

# ----------
# Insight 1: Top Genres by Average Score 
# ----------


def get_top_genres_by_score(db_path):
    with sqlite3.connect(db_path) as conn:
        query = """
            SELECT 
                g.genre, 
                AVG(m.average_score) AS avg_score, 
                COUNT(DISTINCT m.id) AS manga_count
            FROM top_manga as m 
            JOIN top_manga_genres g ON m.id = g.manga_id
            WHERE m.average_score IS NOT NULL 
            GROUP BY g.genre
            HAVING manga_count >= 5
            ORDER BY avg_score DESC
            LIMIT 15
            """
        return pd.read_sql(query, conn)

def plot_top_genres_chart(df):
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("avg_score:Q", title = "Average Score"),
        y=alt.Y("genre:N", sort="-x", title="Genre"),
        tooltip= ["genre", "avg_score", "manga_count"]
    ).properties(
        height=400,
        width = 500, 
        title = "Top 15 Highest-Rated Manga Genres"
    )
    return chart

# ----------
# Main insights view 
# ----------

def show_insights():
    st.title("Insight Dashboard")
    st.markdown("Explore aggregated insights from the top manga dataset.")

    # Load and show insight 1 
    st.header("Top Genres by Average Score")
    genre_df = get_top_genres_by_score(DB_PATH)

    if not genre_df.empty:
        st.altair_chart(plot_top_genres_chart(genre_df), use_container_width=True)
        st.dataframe(genre_df, use_container_width=True)
    else:
        st.warning("No data available for this insight.")
