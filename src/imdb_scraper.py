from imdb import IMDb
import pandas as pd
import gspread
import time
from google import genai

def get_media_details(title, show_title=None):
    ia = IMDb()
    
    print(f"Searching for '{title}' in '{show_title}'")
    
    # Search for the movie or TV show
    movies = ia.search_movie(title)
    if not movies:
        print(f"No results found for '{title}'")
        return None
    
    # Get the correct result
    for movie in movies:
        ia.update(movie, info=['main', 'vote details'])
        if title.lower() in movie.get('title').lower():
            break
    else:
        print(f"No matching title found for '{title}'")
        return None
    
    details = {
        'imdb_code': movie.movieID,
        'title': movie.get('title'),
        'rating': movie.get('rating', 'No rating available'),
        'release_year': movie.get('year', 'No release year available'),
        'cast': [(person['name'], person.currentRole) for person in movie.get('cast', [])],
        'cast_names': [person['name'] for person in movie.get('cast', [])],
        'cast_roles': [person.currentRole for person in movie.get('cast', [])]
    }
    
    return details

def query_gemini_api(prompt, api_key):
    client = genai.Client(api_key=api_key)
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
    
    results = []
    for i in range(5):
        title = df["Name"].iloc[i]
        show_title = df.get("Show/Trilogy", [None]).iloc[i]
        print(title)
        
        # Get IMDb details
        details = get_media_details(title, show_title)
        if details:
            imdb_code = details['imdb_code']
            title = details['title']
            
            # Query Gemini for plot summary
            prompt = (f"Provide a brief plot summary for the following Star Wars media: "
                      f"\nIMDb ID: {imdb_code}\nTitle: {title}\nShow: {show_title}\n")
            print(prompt)
            response = query_gemini_api(prompt, gem_key)
            details['Plot Summary'] = response
            
            results.append(details)
        
        if i % 10 == 0 and i != 0:
            print("Sleeping for 61 seconds")
            time.sleep(61)
    
    results_df = pd.DataFrame(results)
    results_df.to_csv("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\Timeline_with_IMDb.csv", index=False)