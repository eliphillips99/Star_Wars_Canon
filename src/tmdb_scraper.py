import requests
import pandas as pd
import gspread
import time
from google import genai

def get_tmdb_details(title, show_title=None, season=None, episode_num=None, api_key=None):
    base_url = "https://api.themoviedb.org/3"
    
    if show_title not in ['A Star Wars Story', 'Prequel Trilogy', 'Original Trilogy', 'Sequel Trilogy']:
        # Search for the TV show
        search_url = f"{base_url}/search/tv"
        params = {
            "api_key": api_key,
            "query": show_title
        }
        
        response = requests.get(search_url, params=params)
        if response.status_code != 200:
            print(f"No results found for TV show '{show_title}'")
            return None
        
        results = response.json().get('results', [])
        if not results:
            print(f"No results found for TV show '{show_title}'")
            return None
        
        # Get the correct TV show
        for result in results:
            if show_title.lower() in result.get('name', '').lower():
                tv_id = result['id']
                if season and episode_num:
                    season_url = f"{base_url}/tv/{tv_id}/season/{season}"
                    season_response = requests.get(season_url, params={"api_key": api_key, "append_to_response": "credits"})
                    if season_response.status_code == 200:
                        season_data = season_response.json()
                        episode_data = next((ep for ep in season_data['episodes'] if ep['episode_number'] == int(episode_num)), None)
                        if episode_data:
                            episode_data['show_name'] = result.get('name')
                            episode_data['season_air_date'] = season_data.get('air_date', 'No release date available')
                            episode_data['credits'] = season_data.get('credits', {})
                            return episode_data
                else:
                    result['show_name'] = result.get('name')
                    return result
        print(f"No matching show title found for '{show_title}'")
        return None
    else:
        # Search for the movie
        search_url = f"{base_url}/search/movie"
        params = {
            "api_key": api_key,
            "query": title
        }
        
        response = requests.get(search_url, params=params)
        if response.status_code != 200:
            print(f"No results found for '{title}'")
            return None
        
        results = response.json().get('results', [])
        if not results:
            print(f"No results found for '{title}'")
            return None
        
        # Get the correct movie
        for result in results:
            if title.lower() in result.get('title', '').lower():
                movie_id = result['id']
                movie_url = f"{base_url}/movie/{movie_id}"
                movie_response = requests.get(movie_url, params={"api_key": api_key, "append_to_response": "credits"})
                if movie_response.status_code == 200:
                    movie_data = movie_response.json()
                    movie_data['show_name'] = result.get('title')
                    return movie_data
        
        print(f"No matching title found for '{title}'")
        return None

def query_gemini_for_summary(tmdb_id, title, show_title, season, episode_num, api_key):
    client = genai.Client(api_key=api_key)
    if show_title:
        search_query = f"Star Wars {show_title}"
    else:
        search_query = f"Star Wars {title}"
    
    prompt = (f"Provide a brief plot summary for the following Star Wars media: "
              f"\nTMDb ID: {tmdb_id}\nTitle: {search_query}")
    if season and episode_num:
        prompt += f"\nSeason: {season}\nEpisode: {episode_num}"
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text

if __name__ == "__main__":
    # Read the Google Sheets data into a DataFrame
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gspread_API_key.txt","r") as f:
        gspread_key = f.read()
    gc = gspread.api_key(gspread_key)
    
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1PyWmeM1nwzQV6anIfTp9nre5Wg6-eTfFyYBk8R9z4cY/edit?gid=0#gid=0")
    Timeline = sh.worksheet("Timeline")
    data = Timeline.get_all_records()
    df = pd.DataFrame.from_records(data)
    
    # Query Gemini for plot summaries
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gemini_API_key.txt","r") as f:
        gem_key = f.read()
    
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\tmdb_API_key.txt","r") as f:
        tmdb_key = f.read()
    
    results = []
    for i in range(len(df)):
        title = df["Name"].iloc[i]
        show_title = df.get("Show/Trilogy", [None]).iloc[i]
        season = df.get("Season", [None]).iloc[i]
        episode_num = df.get("Episode Num", [None]).iloc[i]
        print(title)
        
        # Get TMDb details
        media = get_tmdb_details(title, show_title, season, episode_num, api_key=tmdb_key)
        if media:
            tmdb_id = media['id']
            first_air_date = media.get('season_air_date') or media.get('release_date', 'No release date available')
            if first_air_date != 'No release date available':
                year, month, _ = first_air_date.split('-')
            else:
                year, month = 'No release year available', 'No release month available'
            
            cast = media.get('credits', {}).get('cast', []) + media.get('credits', {}).get('guest_stars', [])
            cast_details = []
            for person in cast:
                person_details = {
                    'name': person['name'],
                    'character': person['character'],
                    'gender': person.get('gender', 'Unknown')
                }
                cast_details.append(person_details)
            
            details = {
                'tmdb_id': tmdb_id,
                'title': media.get('name') or media.get('title'),
                'show_name': media.get('show_name'),
                'rating': media.get('vote_average', 'No rating available'),
                'tmdb_rating_processed': media.get('vote_average', 0) / 2,
                'release_year': year,
                'release_month': month,
                'cast': cast_details
            }
            
            # Query Gemini for plot summary
            summary = query_gemini_for_summary(tmdb_id, details['title'], show_title, season, episode_num, gem_key)
            details['Plot Summary'] = summary
            
            results.append(details)
        
        if i % 10 == 0 and i != 0:
            print("Sleeping for 61 seconds")
            time.sleep(61)
    
    results_df = pd.DataFrame(results)
    results_df.to_csv("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\Timeline_with_TMDb.csv", index=False)