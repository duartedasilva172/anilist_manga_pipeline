import streamlit as st 
import pandas as pd 
import sqlite3 
import altair as alt 
import sys, os 


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "top_manga.db")


def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        manga_df = pd.read_sql("""
            SELECT m.id, m.title_romaji, m.average_score, m.start_year, m.status,
                    m.chapters, m.volumes, g.genre
            FROM top_manga as m
            LEFT JOIN top_manga_genres g on m.id = g.manga_id
""", conn)
    return manga_df

def show_dashboard():
    st.title("Manga CRUD Explorer")

    df = load_data()
    df.dropna(subset=["average_score"], inplace=True)
    
    # Sidebar filters 
    st.sidebar.header("Filter Options")
    genres = st.sidebar.multiselect("Genres", sorted(df["genre"].dropna().unique()))
    score = st.sidebar.slider("Average Score", 0, 100, (70, 100))
    years = st.sidebar.slider("Start Year", int(df["start_year"].min()), int(df["start_year"].max()), (1980,2023))

    filtered_df =df.copy()
    if genres:
        filtered_df = filtered_df[filtered_df["genre"].isin(genres)]
    filtered_df = filtered_df[
        (filtered_df["average_score"].between(*score)) & 
        (filtered_df["start_year"].between(*years))
    ]

    # Bar Chart 

    st.subheader("Top Manga by Score")
    top_manga = filtered_df.sort_values("average_score", ascending = False).drop_duplicates("id").head(20)

    chart = alt.Chart(top_manga).mark_bar().encode(
        x = alt.X("average_score", title="Score"),
        y = alt.Y("title_romaji", sort="-x", title="Title"),
        tooltip= ["title_romaji", "average_score", "genre"]
    ).properties(height=400)

    st.altair_chart(chart, use_container_width=True)

    # Data Table 

    st.subheader("Filtered Manga List")
    st.dataframe(filtered_df.drop(columns=["id"]), use_container_width=True)