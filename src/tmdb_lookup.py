from tmdb_scraper import get_tmdb_details_id

def lookup_media(tmdb_key):
    """
    Look up a single media entry by TMDB ID and indicate whether it is a show or movie.

    Args:
        tmdb_key (str): The TMDB API key.
    """
    tmdb_id = int(input("Enter the TMDB ID: "))
    is_tv = input("Is this a TV show? (yes/no): ").strip().lower() == "yes"
    details = get_tmdb_details_id(tmdb_id=tmdb_id, api_key=tmdb_key, is_tv=is_tv)

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