from tmdb_scraper import get_tmdb_details
from ai.summary import generate_plot_summary

def lookup_media(tmdb_key, gem_key):
    """
    Look up a single media entry by TMDB ID and fetch all required details.

    Args:
        tmdb_key (str): The TMDB API key.
        gem_key (str): The Gemini API key.
    """
    tmdb_id = int(input("Enter the TMDB ID: "))
    is_tv = input("Is this a TV show? (yes/no): ").strip().lower() == "yes"
    details = get_tmdb_details(tmdb_id=tmdb_id, api_key=tmdb_key, is_tv=is_tv)

    if details:
        # Generate AI plot summary
        plot_summary = generate_plot_summary(details["overview"])
        details["ai_plot_summary"] = plot_summary

        print("Details fetched successfully:")
        print(details)
    else:
        print("Failed to fetch details.")

if __name__ == "__main__":
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\tmdb_API_key.txt", "r") as f:
        tmdb_key = f.read().strip()
    with open("C:\\Users\\eligp\\OneDrive\\Documents\\Coding Projects\\Star_Wars_Canon\\ref\\gemini_API_key.txt", "r") as f:
        gem_key = f.read().strip()

    # Start the lookup process
    lookup_media(tmdb_key, gem_key)