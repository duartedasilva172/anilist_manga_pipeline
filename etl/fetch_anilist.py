import requests 
import json
import pandas as pd 
import pyarrow  # needed for parquet support through pyarrow engine


# December 2 2025: Add Format and popularity metrics

url = "https://graphql.anilist.co"

query = """
query($page: Int, $perPage: Int) {
  Page(page: $page, perPage: $perPage) {
    media(type: MANGA, sort: SCORE_DESC) {
      id
      title {
        romaji
        english
      }
      averageScore
      genres
      startDate {
        year
      }

      # --- NEW FIELDS YOU REQUESTED ---
      status
      chapters
      volumes
      staff {
        nodes {
          name {
            full
            native
          }
          primaryOccupations
        }
      }
      # ----------------------------------
    }

    pageInfo {
      hasNextPage
      currentPage
    }
  }
}
"""

all_manga = []

per_page = 50 

for page in range(1, 7):
    variables = {"page": page, "perPage": per_page}
    resp = requests.post(url, json={"query": query, "variables": variables})
    data = resp.json()
  
    items = data["data"]["Page"]["media"]

    for m in items:
        # Get staff nodes correctly (NO trailing comma)
        staff_nodes = m.get("staff", {}).get("nodes", [])

        # Build a clean list of staff dicts
        staff_compact = [
            {
                "name": s.get("name", {}).get("full"),
                "primaryOccupations": s.get("primaryOccupations", []),
            }
            for s in staff_nodes
            if s.get("name", {}).get("full")
        ]

        # Append one row per manga
        all_manga.append({
            "id": m["id"],
            "title_romaji": m["title"].get("romaji"),
            "title_english": m["title"].get("english"),
            "average_score": m.get("averageScore"),
            "genres": m.get("genres", []),
            "start_year": m.get("startDate", {}).get("year"),
            "status": m.get("status"),
            "chapters": m.get("chapters"),
            "volumes": m.get("volumes"),
            "staff_names": staff_compact,   # stays as staff_names
        })

# Save to Parquet
df = pd.DataFrame(all_manga)
df.to_parquet("data/top_manga.parquet", index=False)
print("Saved Top Mangas to data/top_manga.parquet")
