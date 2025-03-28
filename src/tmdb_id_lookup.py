from tmdb_scraper import get_tmdb_details

# Import the get_tmdb_details function from tmdb_scraper.py

def get_details_by_id(tmdb_id):
    """
    Fetch details of a movie or show using its TMDB ID.

    Args:
        tmdb_id (int): The TMDB ID of the movie or show.

    Returns:
        dict: Details of the movie or show.
    """
    try:
        details = get_tmdb_details(tmdb_id=tmdb_id, api_key=tmdb_id)  # Pass tmdb_id here
        return details
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\tmdb_API_key.txt","r") as f:
        tmdb_key = f.read()
    
    # Example usage
    tmdb_id = int(input("Enter the TMDB ID: "))
    details = get_details_by_id(tmdb_id)
    if details:
        print("Details fetched successfully:")
        print(details)
    else:
        print("Failed to fetch details.")