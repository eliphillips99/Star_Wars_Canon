from tmdb_scraper import get_tmdb_details

def lookup_media(tmdb_key):
    """
    Look up a single media entry by either TMDB ID or name, and indicate whether it is a show or movie.

    Args:
        tmdb_key (str): The TMDB API key.
    """
    choice = input("Would you like to search by (1) ID or (2) Name? Enter 1 or 2: ").strip()
    
    if choice == "1":
        tmdb_id = int(input("Enter the TMDB ID: "))
        is_tv = input("Is this a TV show? (yes/no): ").strip().lower() == "yes"
        details = get_tmdb_details(tmdb_id=tmdb_id, api_key=tmdb_key, show_title="TV" if is_tv else None)
    elif choice == "2":
        title = input("Enter the title of the movie or show: ").strip()
        is_tv = input("Is this a TV show? (yes/no): ").strip().lower() == "yes"
        show_title = title if is_tv else None
        season = input("Enter the season number (or press Enter if not applicable): ").strip()
        episode_num = input("Enter the episode number (or press Enter if not applicable): ").strip()
        
        season = int(season) if season else None
        episode_num = int(episode_num) if episode_num else None
        
        details = get_tmdb_details(title=title, show_title=show_title, season=season, episode_num=episode_num, api_key=tmdb_key)
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return

    if details:
        print("Details fetched successfully:")
        print(details)
    else:
        print("Failed to fetch details.")

if __name__ == "__main__":
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\tmdb_API_key.txt", "r") as f:
        tmdb_key = f.read().strip()  # Ensure the key is stripped of whitespace
    
    # Start the lookup process
    lookup_media(tmdb_key)