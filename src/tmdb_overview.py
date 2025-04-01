import requests
import pandas as pd
import gspread
from tmdb_scraper import get_tmdb_details_id

def get_tmdb_overview(tmdb_id, api_key, is_tv=False):
    """
    Fetch the overview of a movie or TV show from TMDB.

    Args:
        tmdb_id (int): The TMDB ID of the movie or show.
        api_key (str): The TMDB API key.
        is_tv (bool): Whether the ID corresponds to a TV show.

    Returns:
        str: The overview of the movie or show.
    """
    base_url = "https://api.themoviedb.org/3"
    media_url = f"{base_url}/tv/{tmdb_id}" if is_tv else f"{base_url}/movie/{tmdb_id}"
    response = requests.get(media_url, params={"api_key": api_key, "append_to_response": "credits"})
    if response.status_code == 200:
        data = response.json()
        return data.get("overview", "No overview available")
    else:
        response.raise_for_status()
        print(f"Failed to fetch overview for TMDB ID {tmdb_id}")
        return "No overview available"

def load_google_sheet_data(api_key):
    """
    Load data from the Google Sheet.

    Args:
        api_key (str): The gspread API key.

    Returns:
        pd.DataFrame: A DataFrame containing the sheet data.
    """
    gc = gspread.api_key(api_key)
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1PyWmeM1nwzQV6anIfTp9nre5Wg6-eTfFyYBk8R9z4cY/edit?gid=0#gid=0")
    Timeline = sh.worksheet("Timeline")
    data = Timeline.get_all_records()
    return pd.DataFrame.from_records(data)

def main():
    """
    Main function to fetch overviews for all entries in the timeline Google Sheet.
    """
    # Load API keys
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gspread_API_key.txt", "r") as f:
        gspread_key = f.read().strip()
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\tmdb_API_key.txt", "r") as f:
        tmdb_key = f.read().strip()

    # Load Google Sheet data
    df = load_google_sheet_data(gspread_key)

    # Prepare a list to store results
    results = []

    # Loop through each row in the DataFrame
    for _, row in df.iterrows():
        title = row.get("Name")
        tmdb_id = row.get("TMDB ID")
        is_tv = row.get("Type", "").lower() == "tv"  # Assume a "Type" column exists to indicate if it's a TV show

        if not tmdb_id:
            print(f"Skipping {title} due to missing TMDB ID.")
            continue

        # Fetch the details using `get_tmdb_details_id`
        try:
            details = get_tmdb_details_id(tmdb_id, tmdb_key, is_tv=is_tv)
            overview = details.get("overview", "No overview available")
            results.append({"Title": title, "TMDB ID": tmdb_id, "Overview": overview})
        except Exception as e:
            print(f"Error fetching details for {title} (TMDB ID: {tmdb_id}): {e}")

    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)

    # Save the results to a CSV file
    results_df.to_csv("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\Timeline_Overviews.csv", index=False)

    print("Overview fetching completed. Results saved to Timeline_Overviews.csv.")

if __name__ == "__main__":
    main()
