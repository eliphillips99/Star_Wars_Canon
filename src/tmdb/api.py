import requests

BASE_URL = "https://api.themoviedb.org/3"

def search_tmdb(query, api_key, is_tv=False):
    """
    Search for a movie or TV show on TMDb.

    Args:
        query (str): The search query.
        api_key (str): The TMDb API key.
        is_tv (bool): Whether to search for a TV show.

    Returns:
        dict: The search results.
    """
    endpoint = f"{BASE_URL}/search/tv" if is_tv else f"{BASE_URL}/search/movie"
    response = requests.get(endpoint, params={"api_key": api_key, "query": query})
    response.raise_for_status()
    return response.json()

def get_tmdb_details(tmdb_id, api_key, is_tv=False):
    """
    Fetch details of a movie or TV show by TMDb ID.

    Args:
        tmdb_id (int): The TMDb ID.
        api_key (str): The TMDb API key.
        is_tv (bool): Whether the ID corresponds to a TV show.

    Returns:
        dict: The details of the movie or TV show.
    """
    endpoint = f"{BASE_URL}/tv/{tmdb_id}" if is_tv else f"{BASE_URL}/movie/{tmdb_id}"
    response = requests.get(endpoint, params={"api_key": api_key, "append_to_response": "credits"})
    response.raise_for_status()
    return response.json()

def get_episode_release_date(tmdb_id, api_key):
    """
    Fetch the release date of the first episode of a TV show.

    Args:
        tmdb_id (int): The TMDb ID of the TV show.
        api_key (str): The TMDb API key.

    Returns:
        str: The release date of the first episode (YYYY-MM-DD).
    """
    endpoint = f"{BASE_URL}/tv/{tmdb_id}/season/1"
    response = requests.get(endpoint, params={"api_key": api_key})
    response.raise_for_status()
    data = response.json()
    episodes = data.get("episodes", [])
    if episodes:
        return episodes[0].get("air_date", "Unknown")
    return "Unknown"
