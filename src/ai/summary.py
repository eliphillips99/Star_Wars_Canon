import requests
from google import genai
import pandas as pd
import time  # Import time module for delay

def generate_plot_summary(tmdb_id, name, show_name, season_num, episode_num, release_date, overview, is_tv, api_key):
    """
    Generate a plot summary using the Gemini AI model.

    Args:
        tmdb_id (int): The TMDB ID of the media.
        name (str): The title of the media.
        show_name (str): The name of the show (if applicable).
        season_num (int): The season number (if applicable).
        episode_num (int): The episode number (if applicable).
        release_date (str): The release date of the media.
        overview (str): The TMDB overview of the media.
        is_tv (bool): Whether the media is a TV show.
        api_key (str): The Gemini API key.

    Returns:
        str: The generated plot summary.
    """
    client = genai.Client(api_key=api_key)
    prompt = (f"Provide a brief plot summary for the following Star Wars media. The TMDB overview has been provided for context but is not the only source you should use: "
              f"\nTMDb ID: {tmdb_id}\nTitle: {name}\nShow Name: {show_name}"
              f"\nRelease Date: {release_date}\nOverview: {overview}")
    if is_tv:
        prompt += f"\nSeason: {season_num}\nEpisode: {episode_num}"
    
    # Introduce a delay to comply with the rate limit
    time.sleep(4)  # 4 seconds delay ensures no more than 15 calls per minute

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    print(f"AI SUMMARY: {response.text}")
    return response.text

def generate_summaries_from_csv(input_csv, output_csv, api_key):
    """
    Generate AI summaries for entries in a CSV file and save the results to a new CSV.

    Args:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to the output CSV file.
        api_key (str): The Gemini API key.
    """
    # Load the input CSV
    df = pd.read_csv(input_csv)

    # Add a new column for AI summaries
    df["ai_plot_summary"] = df.apply(
        lambda row: generate_plot_summary(
            tmdb_id=row["id"],
            name=row["title"],
            show_name=row.get("show_name", ""),
            season_num=row.get("season", None),
            episode_num=row.get("episode number", None),
            release_date=row.get("release_date", ""),
            overview=row.get("overview", ""),
            is_tv=row.get("media type", "").strip().lower() == "tv",
            api_key=api_key
        ),
        axis=1
    )

    # Save the updated DataFrame to the output CSV
    df.to_csv(output_csv, index=False)
    print(f"AI summaries saved to {output_csv}")