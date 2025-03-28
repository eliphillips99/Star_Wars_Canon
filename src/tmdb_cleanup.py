import pandas as pd
from tmdb_scraper import query_gemini_for_summary, get_tmdb_details
import gspread

# Read the Google Sheets data into a DataFrame
with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gspread_API_key.txt","r") as f:
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
    print(f"Processing: {title}")
    
    # Get TMDB info
    tmdb_info = get_tmdb_details(title)
    
    # Ask for user confirmation
    print(f"Found: {tmdb_info['title']} ({tmdb_info['release_date']})")
    confirmation = input("Is this the correct media? (y/n): ")
    
    if confirmation.lower() == 'y':
        # Query for summary
        summary = query_gemini_for_summary(tmdb_info['id'])
        
        # Store the result
        result = {
            'Title': tmdb_info['title'],
            'Release Date': tmdb_info['release_date'],
            'Summary': summary
        }
        results.append(result)

# Convert results to DataFrame
results_df = pd.DataFrame(results)

# Save to CSV
results_df.to_csv('tmdb_cleanup_results.csv', index=False)

print("Cleanup results saved to tmdb_cleanup_results.csv")