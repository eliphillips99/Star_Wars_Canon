import sys
import os
import pandas as pd

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.google_sheets.sheets import write_dataframe_to_sheet, load_google_sheet_data
from src.tmdb.scraper import find_tmdb_id, process_media_entry
from src.api_config import API_KEYS

def lookup_and_process_row(row, tmdb_key, gem_key):
    """
    Perform a lookup for a single row and process the selected result.

    Args:
        row (pd.Series): A row from the DataFrame containing media details.
        tmdb_key (str): The TMDb API key.
        gem_key (str): The Gemini API key.

    Returns:
        dict: Processed data for the selected result, or None if skipped.
    """
    # Debugging: Print the row being processed
    print(f"\nProcessing row: {row.to_dict()}")

    # Use find_tmdb_id to fetch the TMDb ID and handle TV shows and episodes
    show_id, episode_id, manual_review = find_tmdb_id(row, tmdb_key)
    print(f"TMDb ID: {show_id}, Episode ID: {episode_id}, Manual Review: {manual_review}")  # Debugging output

    if not show_id:
        print(f"No valid TMDb ID found for title: {row['title']}. Skipping.")
        return None

    # Prepare a mock result for manual selection
    search_results = [
        {
            "id": episode_id if episode_id else show_id,
            "title": row["title"],
            "manual_review": manual_review
        }
    ]

    # Display the result for manual verification
    print("\nResult for Verification:")
    for i, result in enumerate(search_results, start=1):
        print(f"{i}. {result.get('title', 'Unknown Title')} (ID: {result['id']})")

    # Let the user select the correct result
    try:
        choice = int(input("\nEnter the number of the correct title (1): "))
        if choice != 1:
            raise ValueError
    except ValueError:
        print(f"Invalid choice for title: {row['title']}. Skipping.")
        return None

    selected_result = search_results[0]
    row["tmdb_id"] = selected_result["id"]

    # Process the media entry
    processed_data = process_media_entry(row, tmdb_key, gem_key, process_gemini=False)
    print(f"Processed data: {processed_data}")  # Debugging output

    if not processed_data:
        print(f"Failed to process the media entry for title: {row['title']}. Skipping.")
        return None

    return processed_data

def process_single_lookup():
    """
    Perform a single lookup for a user-inputted title.
    """
    tmdb_key = API_KEYS["tmdb"]
    gem_key = API_KEYS["gemini"]

    # Get user input for the title
    user_title = input("Enter the title to search for: ").strip()

    # Create a mock row for find_tmdb_id
    row = pd.Series({
        "title": user_title,
        "show/trilogy": None,
        "season": None,
        "episode number": None,
        "media type": "movie"  # Default to movie; adjust if needed
    })

    # Lookup and process the row
    processed_data = lookup_and_process_row(row, tmdb_key, gem_key)
    if not processed_data:
        print("No data processed. Exiting.")
        return

    # Convert the processed data to a DataFrame
    df = pd.DataFrame([processed_data])

    # Debugging: Print the DataFrame before writing to Google Sheets
    print("\nDataFrame to be written:")
    print(df)

    # Write to the "Single Lookup" sheet
    write_dataframe_to_sheet(df, "ref/service_account.json", sheet_name="Single Lookup")

    # Output the processed data
    print("\nProcessed Data:")
    print(df.to_string(index=False))

def process_batch_lookup():
    """
    Perform batch processing for titles in the "Batch Clean" sheet with manual verification.
    """
    tmdb_key = API_KEYS["tmdb"]
    gem_key = API_KEYS["gemini"]

    # Load the "Batch Clean" sheet
    df = load_google_sheet_data(API_KEYS["gspread"], sheet_name="Batch Clean")

    # Ensure the "title" column exists
    if "title" not in df.columns:
        print("The 'Batch Clean' sheet does not contain a 'title' column. Exiting.")
        return

    results = []

    # Loop through each row in the DataFrame
    for _, row in df.iterrows():
        processed_data = lookup_and_process_row(row, tmdb_key, gem_key)
        if processed_data:
            results.append(processed_data)

    # Convert the results to a DataFrame
    results_df = pd.DataFrame(results)

    # Debugging: Print the DataFrame before writing to Google Sheets
    print("\nFinal DataFrame to be written:")
    print(results_df)

    # Write to the "Batch Clean Results" sheet
    write_dataframe_to_sheet(results_df, "ref/service_account.json", sheet_name="Batch Clean Results")

    # Output the processed data
    print("\nBatch Processed Data:")
    print(results_df.to_string(index=False))

def main():
    """
    Main function to allow the user to choose between single lookup or batch processing.
    """
    print("Choose an option:")
    print("1. Single Lookup")
    print("2. Batch Lookup")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        process_single_lookup()
    elif choice == "2":
        process_batch_lookup()
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
