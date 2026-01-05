import streamlit as st 
import numpy as np 
import pandas as pd 
import plotly.express as px 
import os 
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data" 

@st.cache_data
def load_data():

    sales_df = pd.read_csv(DATA_DIR / "combined_data_sales.csv")
    popular_df = pd.read_csv(DATA_DIR / "popular_manga.csv")
    top_df = pd.read_csv(DATA_DIR / "top_manga2.csv")

    # Clean sales circulation

    sales_df["sales_circulation"] = (
    sales_df["sales_circulation"]
    .astype(str)
    .str.replace(",", "", regex=False)
    .astype(float)
)
    
    return sales_df, top_df, popular_df

# sales_df, top_df, popular_df = load_data()


def render_dashboard():

    st.title("Manga Performance Dashboard")

    sales_df, top_df, popular_df = load_data()

    # KPI Row 

    kpi1, kpi2, kpi3 , kpi4 = st.columns(4)

    kpi1.metric("Total Titles", f"{len(sales_df):,}")
    kpi2.metric("Avg Score", f"{sales_df['average_score'].mean():.1f}")
    kpi3.metric("Median Sales", f"{int(sales_df['sales_circulation'].median()):,}")
    kpi4.metric("Avg Chapters", f"{sales_df['chapters'].mean():.0f}")

    # Compute Top Performers

    top_sales = (
        sales_df
        .dropna(subset=["sales_circulation"])
        .sort_values("sales_circulation", ascending=False)
        .iloc[0]
    )

    top_popularity = (
        sales_df
        .dropna(subset=["popularity"])
        .sort_values("popularity", ascending=False)
        .iloc[0]
    )

    # Insert the Top Performer Cards 

    st.subheader("Top Performers")

    tp1, tp2 = st.columns(2)

    with tp1:
        st.markdown("### 💰 Top by Sales")
        st.metric("Title", top_sales["title_romaji"])
        st.metric("Sales", f"{int(top_sales['sales_circulation']):,}")
        st.metric("Chapters", int(top_sales["chapters"]))

    with tp2:
        st.markdown("### 🔥 Most Popular")
        st.metric("Title", top_popularity["title_romaji"])
        st.metric("Popularity Score", int(top_popularity["popularity"]))
        st.metric("Score", top_popularity["average_score"])

        # Sidebar controls
    st.sidebar.header("Filters")

    x_axis = st.sidebar.selectbox(
        "X-axis", 
        ["chapters", "volumes"]
    )

    min_chapters = st.sidebar.slider(
        "Minimum chapters", 
        min_value= 1,
        max_value = int(sales_df["chapters"].max()),
        value=1
    )

    # Prepare clean plotting dataframe

    plot_df = sales_df.copy()

    plot_df = plot_df[
        (plot_df["chapters"].notna()) & 
        (plot_df["volumes"].notna()) & 
        (plot_df["average_score"].notna()) & 
        (plot_df["popularity"].notna()) & 
        (plot_df["sales_circulation"].notna()) & 
        (plot_df["chapters"] >= min_chapters)
        ]

# Correlation 1: Score vs Chapters / Volumes

    fig_score = px.scatter(
        plot_df,
        x = x_axis,
        y = "average_score", 
        hover_name = "title_romaji",
        trendline = "ols",
        labels = {
            "average_score":"Average_score",
            x_axis: x_axis.capitalize()
        }
    )
    
# Correlation 2: Popularity vs Chapters / Volumes 

    fig_popularity = px.scatter(
        plot_df,
        x = x_axis,
        y = "popularity",
        hover_name = "title_romaji",
        trendline = "ols",
        log_y=True,
        labels={
            "popularity": "Popularity (log scale)",
            x_axis: x_axis.capitalize()
        }
    )

    
    
# Wrap existing charts into a grid


    st.divider()

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.subheader("Score vs Length")
        st.plotly_chart(fig_score, use_container_width=True)

    with col2:
        st.subheader("Popularity vs Length")
        st.plotly_chart(fig_popularity, use_container_width=True)