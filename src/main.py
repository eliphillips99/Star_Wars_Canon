from tmdb.scraper import process_all_entries
from google_sheets.sheets import load_google_sheet_data, write_dataframe_to_sheet
from data.output import save_results_to_csv
from api_config import API_KEYS
from ai.summary import generate_summaries_from_csv

def main():
    """
    Main function to orchestrate the workflow for processing TMDb data.
    """

    # Mode 1: Real-time processing
    # Mode 2: Generate summaries from CSV
    mode = 1  # Change this to 2 for summary generation
    if mode == 1:  # Compare to integer
        # Real-time processing logic
        # Load data from Google Sheets
        df = load_google_sheet_data(API_KEYS["gspread"])

        # Specify the number of items to process
        items_to_process = 13  # Change this value to process a different number of entries

        # Process the specified number of entries, remove items_to_process to process all
        results_df = process_all_entries(df, API_KEYS["tmdb"], API_KEYS["gemini"], items_to_process=items_to_process, process_gemini=False)

        # Save results to a CSV
        save_results_to_csv(results_df, "data/Scraped_Timeline.csv")

        # Write results to a new sheet in the original Google Sheet
        write_dataframe_to_sheet(results_df, API_KEYS["gspread"], sheet_name="Scraped Data")
    elif mode == 2:  # Compare to integer
        input_csv = "data/Scraped_Timeline.csv"
        output_csv = "data/Timeline_with_Summaries.csv"
        generate_summaries_from_csv(input_csv, output_csv, API_KEYS["gemini"])
    else:
        print("Invalid mode selected.")

if __name__ == "__main__":
    main()

