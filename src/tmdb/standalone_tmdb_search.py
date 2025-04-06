import sys
import os
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.google_sheets.sheets import write_dataframe_to_sheet  # Adjusted import path
from api import search_tmdb, get_tmdb_details
from utils import extract_cast, extract_genres, extract_character_names
from src.api_config import API_KEYS

def main():
    """
    Standalone script to search TMDb for a user-inputted title, select the correct result,
    and output detailed information for the selected title.
    """
    tmdb_key = API_KEYS["tmdb"]
    user_title = input("Enter the title to search for: ").strip()

    # Search TMDb for the title
    search_results = search_tmdb(query=user_title, api_key=tmdb_key, is_tv=False)
    if not search_results.get("results"):
        print("No results found.")
        return

    # Display the top 5 results
    results = search_results["results"][:5]
    print("\nTop 5 Results:")
    for i, result in enumerate(results, start=1):
        print(f"{i}. {result.get('title', 'Unknown Title')} (ID: {result['id']})")

    # Let the user select the correct result
    try:
        choice = int(input("\nEnter the number of the correct title (1-5): "))
        if choice < 1 or choice > len(results):
            raise ValueError
    except ValueError:
        print("Invalid choice. Exiting.")
        return

    selected_result = results[choice - 1]
    tmdb_id = selected_result["id"]

    # Fetch detailed information for the selected title
    details = get_tmdb_details(tmdb_id, tmdb_key, is_tv=False)
    if not details:
        print("Failed to fetch details for the selected title.")
        return

    # Extract information using existing utility functions
    title = details.get("title", "Unknown Title")
    release_date = details.get("release_date", "Unknown Release Date")
    rating = details.get("vote_average", "N/A")
    genres = extract_genres(details)
    cast = extract_cast(details)
    character_names = extract_character_names(details)
    overview = details.get("overview", "No overview available")

    # Output the information
    print("\nSelected Title Details:")
    print(f"Title: {title}")
    print(f"Release Date: {release_date}")
    print(f"Rating: {rating}")
    print(f"Genres: {', '.join(genres) if genres else 'None'}")
    print(f"Overview: {overview}")
    print("Cast:")
    for actor in cast:
        print(f"  - {actor['name']} as {actor['character']} ({actor['gender']})")
    print(f"Character Names: {', '.join(character_names) if character_names else 'None'}")

    # Prepare data for writing to Google Sheet
    data = {
        "Title": [title],
        "Release Date": [release_date],
        "Rating": [rating],
        "Genres": [', '.join(genres) if genres else 'None'],
        "Overview": [overview],
        "Cast": [', '.join([f"{actor['name']} as {actor['character']} ({actor['gender']})" for actor in cast])],
        "Character Names": [', '.join(character_names) if character_names else 'None']
    }
    df = pd.DataFrame(data)

    # Write to the "Single Lookup" sheet
    write_dataframe_to_sheet(df, "ref/service_account.json", sheet_name="Single Lookup")

if __name__ == "__main__":
    main()
