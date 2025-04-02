from tmdb.api import get_tmdb_details, get_episode_details, search_tmdb
from tmdb.utils import extract_cast, extract_genres, extract_character_names
from ai.summary import generate_plot_summary
import pandas as pd
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def find_tmdb_id(row, tmdb_key):
    """
    Find the TMDB ID for a media entry using title, show/trilogy name, and season/episode number.

    Args:
        row (pd.Series): A row from the DataFrame containing media details.
        tmdb_key (str): The TMDb API key.

    Returns:
        tuple: A tuple containing the show ID (if applicable) and the episode ID (if applicable).
    """
    title = row.get("name")
    show_name = row.get("show/trilogy")
    season = row.get("season")
    episode_num = row.get("episode number")
    media_type = row.get("media type", "").strip().lower()  # Access normalized column name

    # Debugging: Print the media_type value
    print(f"MEDIA TYPE: {media_type}")

    # Determine if the entry is a TV show based on the "Media Type" column
    if media_type == "tv":
        is_tv = True
    elif media_type == "movie":
        is_tv = False
    else:
        print(f"Unknown or missing media type for entry: {row}")
        is_tv = False  # Default to movie if media type is invalid or missing

    # Construct the search query with "Star Wars" prefix
    if is_tv:
        search_query = f"Star Wars {show_name}" if show_name else None
    else:
        search_query = f"Star Wars {title}" if title else None

    if not search_query:
        print("No valid search query could be constructed.")
        return None, None

    print(f"Searching TMDB for query: {search_query} (is_tv={is_tv})")
    search_results = search_tmdb(query=search_query, api_key=tmdb_key, is_tv=is_tv)
    if not search_results.get("results"):
        print(f"No results found for query: {search_query}")
        return None, None

    # Refine the search results
    for result in search_results["results"]:
        show_id = result["id"]
        print(f"TMDB Show ID found: {show_id} (is_tv={is_tv})")

        # Fetch details for the result
        if is_tv and season and episode_num:
            # Fetch episode-specific details using the show ID
            episode_details = get_episode_details(show_id, season, episode_num, tmdb_key)
            if episode_details:
                episode_id = episode_details.get("id")
                print(f"Episode-specific TMDB ID: {episode_id}")
                return show_id, episode_id
        else:
            details = get_tmdb_details(show_id, tmdb_key, is_tv=is_tv)
            if is_tv and details.get("name") == show_name:
                return show_id, None
            elif not is_tv and details.get("title") == title:
                return show_id, None

    print(f"Ambiguous results for query: {search_query}. Please review manually.")
    return None, None

def process_media_entry(row, tmdb_key, gem_key):
    """
    Process a single media entry to fetch TMDb details and AI plot summary.

    Args:
        row (pd.Series): A row from the DataFrame containing media details.
        tmdb_key (str): The TMDb API key.
        gem_key (str): The Gemini API key.

    Returns:
        dict: A dictionary containing processed media details.
    """
    # Find the TMDB ID and determine if it's a TV show
    show_id, episode_id = find_tmdb_id(row, tmdb_key)
    if not show_id:
        print(f"Skipping entry: {row}")
        return None

    print(f"Processing TMDB Show ID: {show_id} (Episode ID: {episode_id})")
    is_tv = row.get("media type", "").strip().lower() == "tv"

    if is_tv and episode_id:
        # Fetch episode-specific details
        episode_data = get_episode_details(show_id, row.get("season"), row.get("episode number"), tmdb_key)
        if not episode_data:
            print(f"Skipping episode ID {episode_id} due to missing data.")
            return None
        title = episode_data.get("name")  # Episode title
        release_date = episode_data.get("air_date")  # Episode air date
        rating = episode_data.get("vote_average")  # Episode rating

        # Fetch show-level details for genres and show_name
        data = get_tmdb_details(show_id, tmdb_key, is_tv=True)
        if not data:
            print(f"Skipping TMDB Show ID {show_id} due to missing show-level data.")
            return None
        show_name = data.get("name")  # Show name
        genres = extract_genres(data)  # Extract genres from show-level data
    else:
        # Fetch show or movie details
        data = get_tmdb_details(show_id, tmdb_key, is_tv=is_tv)
        if not data:
            print(f"Skipping TMDB Show ID {show_id} due to missing data.")
            return None
        title = data["name"] if is_tv else data["title"]  # Show or movie title
        release_date = data.get("release_date")  # Show or movie release date
        rating = data.get("vote_average")  # Show or movie rating
        show_name = None  # No show name for movies
        genres = extract_genres(data)  # Extract genres from movie or show data

    # Extract additional details
    cast = extract_cast(data if not is_tv else episode_data)
    character_names = extract_character_names(data if not is_tv else episode_data)
    overview = data.get("overview", "No overview available") if not is_tv else episode_data.get("overview", "No overview available")

    # Generate plot summary
    plot_summary = generate_plot_summary(
        tmdb_id=episode_id if is_tv else show_id,
        name=title,
        show_name=show_name,
        season_num=row.get("season"),
        episode_num=row.get("episode number"),
        release_date=release_date,
        is_tv=is_tv,
        api_key=gem_key
    )

    return {
        "id": episode_id if is_tv else show_id,  # Use episode ID for TV shows, show ID for movies
        "show_id": show_id if is_tv else None,  # Include show ID for TV shows
        "title": title,  # Episode title for TV shows, movie title for movies
        "show_name": show_name,  # Show name for TV shows
        "release_date": release_date,  # Episode air date for TV shows, release date for movies
        "rating": rating,  # Episode rating for TV shows, movie rating for movies
        "processed_rating": rating / 2 if rating else None,
        "cast": cast,
        "actors": [actor["name"] for actor in cast],
        "genres": genres,  # Populate genres
        "character_names": character_names,
        "overview": overview,
        "ai_plot_summary": plot_summary,  # Include the generated plot summary
    }

def process_all_entries(df, tmdb_key, gem_key, items_to_process=None):
    """
    Process all media entries in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing media details.
        tmdb_key (str): The TMDb API key.
        gem_key (str): The Gemini API key.
        items_to_process (int, optional): The number of entries to process. Defaults to None (process all).

    Returns:
        pd.DataFrame: A DataFrame containing processed media details.
    """
    results = []
    # Limit the DataFrame to the specified number of entries
    rows_to_process = df.head(items_to_process) if items_to_process else df

    for _, row in rows_to_process.iterrows():
        details = process_media_entry(row, tmdb_key, gem_key)
        if details:
            results.append(details)

    # Convert results to a DataFrame
    return pd.DataFrame(results)
