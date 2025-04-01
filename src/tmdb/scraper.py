from tmdb.api import get_tmdb_details, get_episode_release_date, search_tmdb
from tmdb.utils import extract_cast, extract_genres, extract_character_names
from ai.summary import generate_plot_summary
import pandas as pd

def find_tmdb_id(row, tmdb_key):
    """
    Find the TMDB ID for a media entry using title, show/trilogy name, and season/episode number.

    Args:
        row (pd.Series): A row from the DataFrame containing media details.
        tmdb_key (str): The TMDb API key.

    Returns:
        tuple: A tuple containing the TMDB ID and the is_tv flag.
    """
    title = row.get("Name")
    show_name = row.get("Show/Trilogy")
    season = row.get("Season")
    episode_num = row.get("Episode Number")
    media_type = row.get("Media Type", "").strip().lower()  # Normalize to lowercase

    

    # Determine if the entry is a TV show based on the "Media Type" column
    if media_type == "tv":
        is_tv = True
    elif media_type == "movie":
        is_tv = False
    else:
        print(f"Unknown media type for entry: {row}")
        print(media_type)

    # Construct the search query with "Star Wars" prefix
    if is_tv:
        search_query = f"Star Wars {show_name}" if show_name else None
    else:
        search_query = f"Star Wars {title}" if title else None

    if not search_query:
        print("No valid search query could be constructed.")
        return None, is_tv

    print(f"Searching TMDB for query: {search_query} (is_tv={is_tv})")
    search_results = search_tmdb(query=search_query, api_key=tmdb_key, is_tv=is_tv)
    if not search_results.get("results"):
        print(f"No results found for query: {search_query}")
        return None, is_tv

    # Refine the search results
    for result in search_results["results"]:
        tmdb_id = result["id"]

        # Fetch details for the result
        details = get_tmdb_details(tmdb_id, tmdb_key, is_tv=is_tv)

        # Match for TV shows
        if is_tv:
            if details.get("name") == show_name:
                # If season and episode are provided, validate them
                if season and episode_num:
                    episode_date = get_episode_release_date(tmdb_id, tmdb_key)
                    if episode_date:
                        return tmdb_id, is_tv
                else:
                    return tmdb_id, is_tv

        # Match for movies
        else:
            if details.get("title") == title:
                return tmdb_id, is_tv

    print(f"Ambiguous results for query: {search_query}. Please review manually.")
    return None, is_tv

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
    tmdb_id, is_tv = find_tmdb_id(row, tmdb_key)
    if not tmdb_id:
        print(f"Skipping entry: {row}")
        return None

    print(f"Processing TMDB ID: {tmdb_id} (is_tv={is_tv})")
    data = get_tmdb_details(tmdb_id, tmdb_key, is_tv)

    if not data:
        print(f"Skipping TMDB ID {tmdb_id} due to missing data.")
        return None

    cast = extract_cast(data)
    genres = extract_genres(data)
    character_names = extract_character_names(data)
    overview = data.get("overview", "No overview available")
    plot_summary = generate_plot_summary(overview)

    return {
        "id": tmdb_id,
        "title": data["title"],
        "show_name": data.get("name") if is_tv else None,
        "release_date": data.get("release_date"),
        "rating": data.get("vote_average"),
        "processed_rating": data.get("vote_average") / 2 if data.get("vote_average") else None,
        "cast": cast,
        "actors": [actor["name"] for actor in cast],
        "genres": genres,
        "character_names": character_names,
        "overview": overview,
        "ai_plot_summary": plot_summary,
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
