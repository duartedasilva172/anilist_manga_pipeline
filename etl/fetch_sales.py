import pandas as pd
import wikipedia 
import re 
import time 

csv_path = "data/popular_manga.csv"
output_path = "data/popular_manga_sales.csv"

def extract_sales_info(summary_text):
    """ Extract sales or circulation info using regex"""

    # Looks for things like "X million copies"

    match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)(?:\s+million)?\s+copies', summary_text, re.IGNORECASE)
    if match : 
        number = match.group(1).replace(",", "")
        if "million" in match.group(0).lower():
            return float(number) * 1_000_000
        return int(number)
    return None

def fetch_sales_for_title(title):
    """Try to fetch sales or circulation using best search match"""
    try:
        search_results = wikipedia.search(title)
        if not search_results:
            raise Exception("No search results")

        # Try to find the best match manually
        title_keywords = set(title.lower().split())
        for candidate in search_results:
            candidate_keywords = set(candidate.lower().split())
            if title_keywords.issubset(candidate_keywords):
                print(f"✅ Using match: '{candidate}' for '{title}'")
                page = wikipedia.page(candidate, auto_suggest=False, redirect=True)
                sales = extract_sales_info(page.content)
                return sales, page.url

        # If no subset match, fallback to first result
        print(f"⚠️ Fallback match: '{search_results[0]}' for '{title}'")
        page = wikipedia.page(search_results[0])
        sales = extract_sales_info(page.content)
        return sales, page.url

    except Exception as e:
        print(f"[!] Skipped '{title}': {type(e).__name__} - {e}")
        return None, None

 
    
def enrich_with_sales(csv_path, output_path):
    df = pd.read_csv(csv_path)
    df["sales_circulation"] = None
    df["sales_source"] = None

    # Add new columns 
    for idx, row in df.iterrows():
        title = row["title_english"] if pd.notnull(row["title_english"]) else row["title_romaji"]
        print(f"Searching: {title}")
        sales, url = fetch_sales_for_title(title)
        df.at[idx, "sales_circulation"] = sales
        df.at[idx, "sales_source"] = url 
        time.sleep(1) 
    
    df.to_csv(output_path, index= False)
    print(f"\nDone! Updated CSV saved to: {output_path}")

if __name__ == "__main__":
    enrich_with_sales(csv_path, output_path)