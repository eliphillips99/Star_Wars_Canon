import pandas as pd
from tmdb_scraper import get_tmdb_details, query_gemini_for_summary
import gspread

# Read the Google Sheets data into a DataFrame
with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gspread_API_key.txt", "r") as f:
    gspread_key = f.read()
gc = gspread.api_key(gspread_key)

sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1PyWmeM1nwzQV6anIfTp9nre5Wg6-eTfFyYBk8R9z4cY/edit?gid=0#gid=0")
Timeline = sh.worksheet("Timeline")
data = Timeline.get_all_records()
df = pd.DataFrame.from_records(data)

# Filter rows marked for cleanup
cleanup_df = df[df['Marked for Cleanup'] == 'x']

# List to store results
results = []

# Process each row marked for cleanup
for index, row in cleanup_df.iterrows():
    title = row['Name']
    show_title = 'Star Wars ' + str(row.get('Show/Trilogy', None))
    season = row.get('Season', None)
    episode_num = row.get('Episode Num', None)  # Re-add episode number
    print(f"Processing: {title}")
    
    # Get TMDB info
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\tmdb_API_key.txt", "r") as f:
        tmdb_key = f.read()

    # Include episode number in the query
    tmdb_info = get_tmdb_details(title, show_title, season, episode_num, api_key=tmdb_key)
    
    if not tmdb_info:
        print(f"No TMDB information found for {title}")
        continue
    
    # Handle single or multiple results
    tmdb_results = tmdb_info if isinstance(tmdb_info, list) else [tmdb_info]
    
    for tmdb_result in tmdb_results:
        if not isinstance(tmdb_result, dict):
            print(f"Invalid TMDB result format for {title}")
            continue
        
        # Safely access the title, show name, and release year
        tmdb_title = tmdb_result.get('title') or tmdb_result.get('name', 'Unknown Title')
        show_name = tmdb_result.get('show_name', 'Unknown Show')
        release_date = tmdb_result.get('release_date') or tmdb_result.get('season_air_date', 'No release date available')
        release_year = release_date.split('-')[0] if release_date != 'No release date available' else 'Unknown Year'
        
        # Ask for user confirmation
        print(f"Found: Title: {tmdb_title}, Show: {show_name}, Release Year: {release_year}")
        confirmation = input("Is this the correct media? (y/n): ")
        
        if confirmation.lower() == 'y':
            # Extract details
            tmdb_id = tmdb_result['id']
            rating = tmdb_result.get('vote_average', 'No rating available')
            processed_rating = rating / 2 if isinstance(rating, (int, float)) else 'No processed rating available'
            release_month = release_date.split('-')[1] if release_date != 'No release date available' else 'Unknown Month'
            cast = tmdb_result.get('credits', {}).get('cast', []) + tmdb_result.get('credits', {}).get('guest_stars', [])
            cast_details = [{'name': person['name'], 'character': person['character'], 'gender': person.get('gender', 'Unknown')} for person in cast]
            
            with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gemini_API_key.txt", "r") as f:
                gem_key = f.read()
            # Query for summary
            summary = query_gemini_for_summary(tmdb_id, tmdb_title, show_title, season, episode_num, api_key=gem_key)
            
            # Store the result
            result = {
                'TMDB ID': tmdb_id,
                'Title': tmdb_title,
                'Show': show_name,
                'Rating': rating,
                'Processed Rating': processed_rating,
                'Release Year': release_year,
                'Release Month': release_month,
                'Cast': cast_details,
                'Plot Summary': summary
            }
            results.append(result)
            break
        else:
            print("Trying the next result...")
    else:
        print(f"No correct match found for {title}")

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save to CSV
results_df.to_csv("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\data\\tmdb_cleanup_results.csv", index=False)

print("Cleanup results saved to tmdb_cleanup_results.csv")