import requests
import pandas as pd
import gspread
import time
from google import genai
from tmdb_overview import get_tmdb_overview
from tmdb.api import get_tmdb_details
from tmdb.utils import extract_cast, extract_genres, extract_character_names
from ai.summary import generate_plot_summary

def get_tmdb_details_id(tmdb_id, api_key, is_tv=False):
    """
    Fetch details directly using the TMDB ID and return a simplified dictionary.

    Args:
        tmdb_id (int): The TMDB ID of the movie or show.
        api_key (str): The TMDB API key.
        is_tv (bool): Whether the ID corresponds to a TV show.

    Returns:
        dict: Simplified details of the movie or show.
    """
    base_url = "https://api.themoviedb.org/3"
    media_url = f"{base_url}/tv/{tmdb_id}" if is_tv else f"{base_url}/movie/{tmdb_id}"
    response = requests.get(media_url, params={"api_key": api_key, "append_to_response": "credits"})
    if response.status_code == 200:
        data = response.json()
        return {
            "id": data.get("id"),
            "title": data.get("name") if is_tv else data.get("title"),
            "release_date": data.get("first_air_date") if is_tv else data.get("release_date"),
            "rating": data.get("vote_average"),
            "cast": [
                {"name": person.get("name"), "character": person.get("character"), "gender": person.get("gender")}
                for person in data.get("credits", {}).get("cast", [])
            ]
        }
    else:
        print(f"Failed to fetch details for TMDB ID {tmdb_id}")
        return None


def get_tmdb_details_name(title=None, show_title=None, season=None, episode_num=None, api_key=None):
    """
    Fetch details by searching for a title and return a simplified dictionary.

    Args:
        title (str): The title of the movie.
        show_title (str): The title of the TV show or miniseries.
        season (int): The season number (for TV shows).
        episode_num (int): The episode number (for TV shows).
        api_key (str): The TMDB API key.

    Returns:
        dict: Simplified details of the movie or show.
    """
    base_url = "https://api.themoviedb.org/3"
    is_tv = show_title not in ['A Star Wars Story', 'Prequel Trilogy', 'Original Trilogy', 'Sequel Trilogy']

    if is_tv:
        # Search for the TV show or miniseries
        search_url = f"{base_url}/search/tv"
        params = {"api_key": api_key, "query": show_title}
        response = requests.get(search_url, params=params)
        if response.status_code != 200 or not response.json().get('results', []):
            print(f"No results found for TV show or miniseries '{show_title}'")
            return None

        # Get the correct TV show or miniseries
        tv_id = response.json()['results'][0]['id']
        if season and episode_num:
            season_url = f"{base_url}/tv/{tv_id}/season/{season}"
            season_response = requests.get(season_url, params={"api_key": api_key})
            if season_response.status_code == 200:
                season_data = season_response.json()
                episode_data = next(
                    (ep for ep in season_data['episodes'] if ep['episode_number'] == int(episode_num)), None
                )
                if episode_data:
                    return {
                        "id": episode_data.get("id"),
                        "title": episode_data.get("name"),
                        "air_date": episode_data.get("air_date"),
                        "season": season,
                        "episode": episode_num
                    }
        else:
            tv_url = f"{base_url}/tv/{tv_id}"
            tv_response = requests.get(tv_url, params={"api_key": api_key})
            if tv_response.status_code == 200:
                data = tv_response.json()
                return {
                    "id": data.get("id"),
                    "title": data.get("name"),
                    "release_date": data.get("first_air_date"),
                    "rating": data.get("vote_average"),
                    "cast": [
                        {"name": person.get("name"), "character": person.get("character"), "gender": person.get("gender")}
                        for person in data.get("credits", {}).get("cast", [])
                    ]
                }
    else:
        # Search for the movie
        search_url = f"{base_url}/search/movie"
        params = {"api_key": api_key, "query": title}
        response = requests.get(search_url, params=params)
        if response.status_code != 200 or not response.json().get('results', []):
            print(f"No results found for '{title}'")
            return None

        # Get the correct movie
        movie_id = response.json()['results'][0]['id']
        movie_url = f"{base_url}/movie/{movie_id}"
        movie_response = requests.get(movie_url, params={"api_key": api_key})
        if movie_response.status_code == 200:
            data = movie_response.json()
            return {
                "id": data.get("id"),
                "title": data.get("title"),
                "release_date": data.get("release_date"),
                "rating": data.get("vote_average"),
                "cast": [
                    {"name": person.get("name"), "character": person.get("character"), "gender": person.get("gender")}
                    for person in data.get("credits", {}).get("cast", [])
                ]
            }

    print(f"No matching title found for '{title}'")
    return None


def get_tmdb_details(title=None, show_title=None, season=None, episode_num=None, api_key=None, tmdb_id=None):
    """
    Wrapper function to fetch TMDB details either by ID or by name.

    Args:
        title (str): The title of the movie.
        show_title (str): The title of the TV show or miniseries.
        season (int): The season number (for TV shows).
        episode_num (int): The episode number (for TV shows).
        api_key (str): The TMDB API key.
        tmdb_id (int): The TMDB ID of the movie or show.

    Returns:
        dict: Details of the movie or show.
    """
    if tmdb_id:
        is_tv = show_title not in ['A Star Wars Story', 'Prequel Trilogy', 'Original Trilogy', 'Sequel Trilogy']
        return get_tmdb_details_id(tmdb_id, api_key, is_tv)
    else:
        return get_tmdb_details_name(title, show_title, season, episode_num, api_key)


def query_gemini_for_summary(tmdb_id, title, show_title, season, episode_num, api_key):
    client = genai.Client(api_key=api_key)
    if show_title not in ['A Star Wars Story', 'Prequel Trilogy', 'Original Trilogy', 'Sequel Trilogy']:
        search_query = f"Star Wars {show_title}"
    else:
        search_query = f"Star Wars {title}"
    
    prompt = (f"Provide a brief plot summary for the following Star Wars media: "
              f"\nTMDb ID: {tmdb_id}\nTitle: {search_query}")
    if season and episode_num:
        prompt += f"\nSeason: {season}\nEpisode: {episode_num}"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text


def load_api_keys():
    """
    Load API keys from files.

    Returns:
        dict: A dictionary containing API keys for gspread, TMDB, and Gemini.
    """
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gspread_API_key.txt", "r") as f:
        gspread_key = f.read()
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\tmdb_API_key.txt", "r") as f:
        tmdb_key = f.read()
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gemini_API_key.txt", "r") as f:
        gem_key = f.read()
    return {"gspread": gspread_key, "tmdb": tmdb_key, "gemini": gem_key}


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
    tmdb_id = row["TMDB ID"]
    is_tv = row.get("Type", "").lower() == "tv"
    data = get_tmdb_details(tmdb_id, tmdb_key, is_tv)

    if not data:
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


def process_all_entries(df, tmdb_key, gem_key):
    """
    Process all media entries in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing media details.
        tmdb_key (str): The TMDB API key.
        gem_key (str): The Gemini API key.

    Returns:
        list: A list of dictionaries containing processed media details.
    """
    results = []
    for i, row in df.iterrows():
        details = process_media_entry(row, tmdb_key, gem_key)
        if details:
            results.append(details)

        if i % 10 == 0 and i != 0:
            print("Sleeping for 61 seconds")
            time.sleep(61)
    return results


def save_results_to_csv(results, output_path):
    """
    Save the processed results to a CSV file.

    Args:
        results (list): A list of dictionaries containing processed media details.
        output_path (str): The file path to save the CSV.
    """
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_path, index=False)


def main():
    """
    Main function to orchestrate the processing of media entries.
    """
    api_keys = load_api_keys()
    df = load_google_sheet_data(api_keys["gspread"])
    
    # Variable to control how many entries to process
    max_entries = input("Enter the number of entries to process (or press Enter to process all): ").strip()
    max_entries = int(max_entries) if max_entries else len(df)
    df = df.head(max_entries)  # Limit the DataFrame to the specified number of entries

    results = process_all_entries(df, api_keys["tmdb"], api_keys["gemini"])
    save_results_to_csv(results, "C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\Timeline_with_TMDb.csv")


if __name__ == "__main__":
    main()