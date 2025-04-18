import sys
import os
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.google_sheets.sheets import write_dataframe_to_sheet
from api import get_tmdb_details, get_episode_details, get_season_details  # Import get_season_details
from utils import extract_cast, extract_genres, extract_character_names
from src.api_config import API_KEYS

def fetch_and_process_details(is_tv, tmdb_id, season=None, episode=None):
    """
    Fetch and process details for a TV show episode or movie.

    Args:
        is_tv (bool): Whether the input is for a TV show.
        tmdb_id (int): The TMDb ID of the show or movie.
        season (int, optional): The season number (for TV shows).
        episode (int, optional): The episode number (for TV shows).

    Returns:
        dict: Processed data for the selected result, or None if failed.
    """
    tmdb_key = API_KEYS["tmdb"]

    if is_tv:
        if season is None or episode is None:
            print("Season and episode numbers are required for TV shows.")
            return None

        # Fetch episode details
        print(f"Fetching details for Show ID: {tmdb_id}, Season: {season}, Episode: {episode}")
        details = get_episode_details(tmdb_id, season, episode, tmdb_key)  # Use get_episode_details
    else:
        # Fetch movie details
        print(f"Fetching details for Movie ID: {tmdb_id}")
        details = get_tmdb_details(tmdb_id, tmdb_key, is_tv=False)

    if not details:
        print("Failed to fetch details.")
        return None

    # Debugging: Print the raw details to inspect the structure
    print("\nRaw Details:")
    print(details)

    # Extract genres and debug the output
    genres = extract_genres(details)
    print("\nExtracted Genres:")
    print(genres)

    # Extract cast, actors, and character names
    cast = extract_cast(details)  # Returns a list of dictionaries
    actors = [actor["name"] for actor in cast]  # Extract actor names as a list
    character_names = [actor["character"] for actor in cast]  # Extract character names as a list

    # Debugging: Print the extracted cast, actors, and character names
    print("\nExtracted Cast:")
    print(cast)
    print("\nExtracted Actors:")
    print(actors)
    print("\nExtracted Character Names:")
    print(character_names)

    # Extract other information using existing utility functions
    id = details.get("id")
    show_id = tmdb_id if is_tv else None
    title_y = details.get("name") if is_tv else details.get("title", "Unknown Title")
    show_name = details.get("show_name") if is_tv else None
    release_date = details.get("air_date") if is_tv else details.get("release_date", "Unknown Release Date")
    tmdb_rating = details.get("vote_average", None)
    processed_rating = tmdb_rating / 2 if tmdb_rating else None
    overview = details.get("overview", "No overview available")

    return {
        "id": id,
        "show_id": show_id,
        "title_y": title_y,
        "show_name": show_name,
        "release_date": release_date,
        "tmdb_rating": tmdb_rating,
        "processed_rating": processed_rating,
        "cast": cast,  # List of dictionaries
        "actors": actors,  # List of actor names
        "genres": genres,  # List of genres
        "character_names": character_names,  # List of character names
        "overview": overview
    }

def fetch_and_process_season(tmdb_id, season):
    """
    Fetch and process all episodes of a season for a given show.

    Args:
        tmdb_id (int): The TMDb ID of the show.
        season (int): The season number.

    Returns:
        list: A list of dictionaries containing processed data for each episode.
    """
    tmdb_key = API_KEYS["tmdb"]

    # Fetch season details
    print(f"Fetching details for Show ID: {tmdb_id}, Season: {season}")
    season_details = get_season_details(tmdb_id, season, tmdb_key)  # Use get_season_details
    if not season_details or "episodes" not in season_details:
        print(f"Failed to fetch details for Show ID: {tmdb_id}, Season: {season}")
        return []

    episodes = season_details["episodes"]
    results = []

    # Process each episode
    for episode in episodes:
        episode_number = episode.get("episode_number")
        print(f"Processing Episode {episode_number} of Season {season}")

        # Fetch episode details
        details = get_episode_details(tmdb_id, season, episode_number, tmdb_key)
        if not details:
            print(f"Failed to fetch details for Episode {episode_number}. Skipping.")
            continue

        # Extract information using existing utility functions
        id = details.get("id")
        show_id = tmdb_id
        title_y = details.get("name", "Unknown Title")
        show_name = season_details.get("name", "Unknown Show")
        release_date = details.get("air_date", "Unknown Release Date")
        tmdb_rating = details.get("vote_average", None)
        processed_rating = tmdb_rating / 2 if tmdb_rating else None
        genres = extract_genres(details)
        cast = extract_cast(details)  # Returns a list of dictionaries
        actors = [actor["name"] for actor in cast]  # Extract actor names as a list
        character_names = [actor["character"] for actor in cast]  # Extract character names as a list
        overview = details.get("overview", "No overview available")

        # Append processed data for the episode
        results.append({
            "id": id,
            "show_id": show_id,
            "title_y": title_y,
            "show_name": show_name,
            "release_date": release_date,
            "tmdb_rating": tmdb_rating,
            "processed_rating": processed_rating,
            "cast": cast,  # List of dictionaries
            "actors": actors,  # List of actor names
            "genres": genres,  # List of genres
            "character_names": character_names,  # List of character names
            "overview": overview
        })

    return results

def main():
    """
    Main function to fetch details for a TV show episode, movie, or all episodes of a season.
    """
    print("Choose the type of operation:")
    print("1. Single TV Show Episode")
    print("2. Single Movie")
    print("3. All Episodes of a Season")
    choice = input("Enter your choice (1, 2, or 3): ").strip()

    if choice == "1":
        is_tv = True
        tmdb_id = int(input("Enter the TMDb Show ID: ").strip())
        season = int(input("Enter the Season Number: ").strip())
        episode = int(input("Enter the Episode Number: ").strip())
        processed_data = fetch_and_process_details(is_tv, tmdb_id, season, episode)
        if not processed_data:
            print("No data processed. Exiting.")
            return
        df = pd.DataFrame([processed_data])
    elif choice == "2":
        is_tv = False
        tmdb_id = int(input("Enter the TMDb Movie ID: ").strip())
        processed_data = fetch_and_process_details(is_tv, tmdb_id)
        if not processed_data:
            print("No data processed. Exiting.")
            return
        df = pd.DataFrame([processed_data])
    elif choice == "3":
        tmdb_id = int(input("Enter the TMDb Show ID: ").strip())
        season = int(input("Enter the Season Number: ").strip())
        processed_data = fetch_and_process_season(tmdb_id, season)
        if not processed_data:
            print("No data processed. Exiting.")
            return
        df = pd.DataFrame(processed_data)
    else:
        print("Invalid choice. Exiting.")
        return

    # Write to the "Single Lookup" sheet
    write_dataframe_to_sheet(df, "ref/service_account.json", sheet_name="Single Lookup")

    # Output the processed data
    print("\nProcessed Data:")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
