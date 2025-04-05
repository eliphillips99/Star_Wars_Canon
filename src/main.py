from tmdb.scraper import process_all_entries
from google_sheets.sheets import load_google_sheet_data
from data.output import save_results_to_csv
from api_config import API_KEYS

def main():
    """
    Main function to orchestrate the workflow for processing TMDb data.
    """
    # Load data from Google Sheets
    df = load_google_sheet_data(API_KEYS["gspread"])

    # Specify the number of items to process
    items_to_process = 13  # Change this value to process a different number of entries

    # Process the specified number of entries, remove items_to_process to process all
    # results_df = process_all_entries(df, API_KEYS["tmdb"], API_KEYS["gemini"])
    results_df = process_all_entries(df, API_KEYS["tmdb"], API_KEYS["gemini"], items_to_process=items_to_process, process_gemini=False)

    # Save results to a CSV
    save_results_to_csv(results_df, "data/Timeline_with_TMDb.csv")

if __name__ == "__main__":
    main()

