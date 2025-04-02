import gspread
import pandas as pd

def load_google_sheet_data(api_key):
    """
    Load data from the Google Sheet.

    Args:
        api_key (str): The gspread API key.

    Returns:
        pd.DataFrame: A DataFrame containing the sheet data.
    """
    gc = gspread.api_key(api_key)
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1PyWmeM1nwzQV6anIfTp9nre5Wg6-eTfFyYBk8R9z4cY/edit")
    worksheet = sh.worksheet("Timeline")
    data = worksheet.get_all_records()  # Import all data without specifying headers
    df = pd.DataFrame(data)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # Debugging: Print the normalized column names and the first few rows
    print("Normalized DataFrame Columns:", df.columns.tolist())
    print("First Few Rows of DataFrame:\n", df.head())

    return df
