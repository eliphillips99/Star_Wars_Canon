import requests
from google import genai

def generate_plot_summary(tmdb_id, name, show_name, season_num, episode_num, release_date, is_tv, api_key):
    client = genai.Client(api_key=api_key)
    
    prompt = (f"Provide a brief plot summary for the following Star Wars media: "
              f"\nTMDb ID: {tmdb_id}\nTitle: {name}\nShow Name: {show_name}"
              f"{episode_num}\nRelease Date: {release_date}\n")
    if is_tv:
        prompt += f"\nSeason: {season_num}\nEpisode: {episode_num}"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text