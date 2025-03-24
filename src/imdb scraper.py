from imdb import Cinemagoer
import pandas as pd
import os

def get_movie_details(title, episode_title=None):
    ia = Cinemagoer()
    
    # Search for the movie or TV show
    movies = ia.search_movie(title)
    
    if not movies:
        print(f"No results found for '{title}'")
        return None
    
    # Get the first result
    movie = movies[0]
    ia.update(movie, info=['main', 'plot', 'rating'])
    
    if episode_title:
        # Search for the episode within the TV show
        episodes = ia.search_episode(title, episode_title)
        if not episodes:
            print(f"No results found for episode '{episode_title}' in '{title}'")
            return None
        episode = episodes[0]
        ia.update(episode, info=['main', 'plot', 'rating'])
        movie = episode
    
    details = {
        'title': movie.get('title'),
        'plot': movie.get('plot', ['No plot summary available'])[0],
        'rating': movie.get('rating', 'No rating available'),
        'cast': [(person['name'], person.currentRole) for person in movie.get('cast', [])],
        'cast_names': [person['name'] for person in movie.get('cast', [])],
        'cast_roles': [person.currentRole for person in movie.get('cast', [])]
    }
    
    return details

def process_titles(df):
    ia = Cinemagoer()
    results = []
    
    for i in range(len(df)):

        if df["Show/Trilogy"][i]:
            show_title = df["Show/Trilogy"][i]
            episode_title = df.get("Name", [None])[i]
            details = get_movie_details(show_title, episode_title)
            if details:
                results.append(details)
        
        else:
            title = df["Name"][i]
            details = get_movie_details(title)
            if details:
                results.append(details)
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    # Read the CSV file into a DataFrame
    df = pd.read_csv("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\Timeline.csv")
    # data = {'Title': ['Star Wars', 'The Empire Strikes Back', 'Friends'], 'Episode': [None, None, 'The One Where It All Began']}
    
    
    results_df = process_titles(df)
    print(results_df)