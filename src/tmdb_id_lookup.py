from tmdb_scraper import get_tmdb_details

def lookup_media(tmdb_key):
    """
    Look up a single media entry by either TMDB ID or name.

    Args:
        tmdb_key (str): The TMDB API key.
    """
    choice = input("Would you like to search by (1) ID or (2) Name? Enter 1 or 2: ").strip()
    
    if choice == "1":
        tmdb_id = int(input("Enter the TMDB ID: "))
        details = get_tmdb_details(tmdb_id=tmdb_id, api_key=tmdb_key)
    elif choice == "2":
        title = input("Enter the title of the movie: ").strip()
        show_title = input("Enter the show title (or press Enter if not applicable): ").strip() or None
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