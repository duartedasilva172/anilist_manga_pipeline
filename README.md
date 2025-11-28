# 📊 AniList Manga Pipeline

This project builds a lightweight data pipeline to fetch, transform, and explore top manga data using Python, SQLite, and Streamlit.

---

## 🔧 Features

- 🗃️ Ingest top manga data from external APIs
- 🧼 Clean and transform the data
- 💾 Store it in a local SQLite database
- 🧪 Query the database using a **Streamlit SQL Workbench**

> **Note:** Dashboard visualizations are coming soon!

---

## 🗂️ Project Structure

manga_data_pipeline/
├── data/ # Raw input data (e.g. CSV)
├── db/ # SQLite database
├── etl/ # Scripts to fetch and process manga data
├── streamlit_app/ # Streamlit interface
│ └── app.py
├── .venv/ # Virtual environment (not tracked)
├── requirements.txt
└── README.md


## 🚀 How to Run

1. **Clone the repo:**
   git clone https://github.com/duartedasilva172/anilist_manga_pipeline.git
   cd anilist_manga_pipeline
Create a virtual environment:


python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies:


pip install -r requirements.txt
Run the Streamlit app:


streamlit run streamlit_app/app.py
🧠 Tech Stack
Python 3.9

Streamlit – for interactive UI

Pandas – for data transformation

SQLite3 – for lightweight SQL database

📌 To Do
📈 Build dashboard with key insights (genres, rankings, scores)

🔍 Add filter and search options in UI

🧪 Write tests for ETL and database logic

📬 Contact
Made by @duartedasilva172
Feel free to fork, clone, or reach out for collaboration!

yaml
Copy code

---

### ✅ Next Step

Save this as `README.md` in the root of your repo.  
Then commit:

```bash
git add README.md
git commit -m "Add README with project overview and setup"
git push